const axios = require('axios');
const chalk = require('chalk');
const fs = require('fs-extra');
const prompts = require('prompts');
const { exec } = require('child_process');
const path = require('path');
const os = require('os');

// ============================================
// CONFIGURAÇÕES SEGURAS
// ============================================

const CONFIG = {
    OLLAMA_URL: 'http://localhost:11434/api/chat',
    MODEL: 'qwen2.5-coder:7b',
    LOG_FILE: path.join(__dirname, `agent_log_${Date.now()}.md`),
    MAX_ITERATIONS: 15,           // ✅ Limite de iterações
    MAX_COST_USD: 0.50,           // ✅ Limite de custo
    MAX_TOKENS_PER_REQUEST: 4096, // ✅ Limite de tokens
    
    // ✅ WORKSPACE via variável de ambiente ou configuração
    WORKSPACE_DIR: process.env.AGENT_WORKSPACE || path.join(os.homedir(), 'agent_workspace'),
    
    // ✅ TIMEOUT para operações
    COMMAND_TIMEOUT: 30000, // 30 segundos
    HTTP_TIMEOUT: 60000      // 60 segundos
};

// ============================================
// LISTA DE COMANDOS PERMITIDOS (WHITELIST)
// ============================================

const ALLOWED_COMMANDS = {
    // Comandos de leitura
    read: ['ls', 'dir', 'cat', 'head', 'tail', 'wc', 'find', 'tree', 'pwd'],
    
    // Comandos de git (somente leitura)
    git: ['git status', 'git log', 'git diff', 'git branch', 'git show'],
    
    // Comandos de Python
    python: ['python --version', 'python3 --version', 'pip list'],
    
    // Comandos de Node
    node: ['node --version', 'npm list', 'npm --version'],
    
    // Nenhum comando destrutivo permitido!
};

// ============================================
// ARQUIVOS E DIRETÓRIOS PROTEGIDOS
// ============================================

const DENIED_PATHS = [
    // Credenciais do sistema
    path.join(os.homedir(), '.aws'),
    path.join(os.homedir(), '.ssh'),
    path.join(os.homedir(), '.gnupg'),
    path.join(os.homedir(), '.kube'),
    path.join(os.homedir(), '.azure'),
    path.join(os.homedir(), '.config', 'gcloud'),
    path.join(os.homedir(), '.docker', 'config.json'),
    path.join(os.homedir(), '.npmrc'),
    path.join(os.homedir(), '.netrc'),
    path.join(os.homedir(), '.vault-token'),
    
    // Arquivos de ambiente
    '.env',
    '.env.local',
    '.env.*',
    'credentials.json',
    'serviceAccountKey.json',
    '*.pem',
    '*.key',
];

// ============================================
// VARIÁVEIS DE AMBIENTE SENSÍVEIS
// ============================================

const SENSITIVE_ENV_VARS = [
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'AWS_SESSION_TOKEN',
    'AZURE_CLIENT_SECRET',
    'GOOGLE_APPLICATION_CREDENTIALS',
    'GITHUB_TOKEN',
    'GH_TOKEN',
    'NPM_TOKEN',
    'ANTHROPIC_API_KEY',
    'OPENAI_API_KEY',
    'DATABASE_URL',
    'VAULT_TOKEN',
    'DOCKER_PASSWORD'
];

// ============================================
// SANITIZAÇÃO DE AMBIENTE
// ============================================

function sanitizeEnvironment() {
    // ✅ Remove variáveis sensíveis do ambiente
    SENSITIVE_ENV_VARS.forEach(varName => {
        if (process.env[varName]) {
            delete process.env[varName];
        }
    });
    
    // ✅ Define ambiente limpo para subprocessos
    process.env.NODE_ENV = process.env.NODE_ENV || 'production';
    
    console.log(chalk.green('✓ Ambiente sanitizado - credenciais removidas'));
}

// ============================================
// VALIDAÇÃO DE CAMINHOS
// ============================================

function validatePath(inputPath, operation = 'read') {
    const resolvedPath = path.resolve(inputPath);
    const normalizedPath = path.normalize(resolvedPath);
    
    // ✅ Verifica se está dentro do workspace permitido
    const workspacePath = path.resolve(CONFIG.WORKSPACE_DIR);
    if (!normalizedPath.startsWith(workspacePath)) {
        throw new Error(`Acesso negado: caminho fora do workspace permitido. Workspace: ${workspacePath}`);
    }
    
    // ✅ Verifica lista de negação
    for (const deniedPath of DENIED_PATHS) {
        if (normalizedPath.includes(deniedPath) || normalizedPath.endsWith(deniedPath)) {
            throw new Error(`Acesso negado: caminho protegido: ${deniedPath}`);
        }
    }
    
    // ✅ Previne path traversal
    if (normalizedPath.includes('..')) {
        throw new Error('Path traversal detectado: caminho inválido');
    }
    
    // ✅ Verifica existência para leitura
    if (operation === 'read' && !fs.existsSync(normalizedPath)) {
        throw new Error(`Arquivo não encontrado: ${normalizedPath}`);
    }
    
    return normalizedPath;
}

// ============================================
// VALIDAÇÃO DE COMANDOS
// ============================================

function validateCommand(command) {
    const trimmedCmd = command.trim();
    const baseCmd = trimmedCmd.split(/\s+/)[0].toLowerCase();
    
    // ✅ Verifica lista de permissão
    let isAllowed = false;
    for (const category in ALLOWED_COMMANDS) {
        if (ALLOWED_COMMANDS[category].includes(baseCmd) || 
            ALLOWED_COMMANDS[category].some(allowed => trimmedCmd.startsWith(allowed))) {
            isAllowed = true;
            break;
        }
    }
    
    if (!isAllowed) {
        throw new Error(`Comando não permitido: ${baseCmd}. Comandos permitidos: ${JSON.stringify(ALLOWED_COMMANDS, null, 2)}`);
    }
    
    // ✅ Bloqueia operadores perigosos
    const dangerousPatterns = [
        /[;&|`$]/,           // Shell operators
        /\brm\s+-rf\b/,      // rm -rf
        /\bsudo\b/,          // sudo
        /\bchmod\b/,         // chmod
        /\bchown\b/,         // chown
        /\bcurl.*\|/,        // curl | bash
        /\bwget.*\|/,        // wget | sh
        />\s*\//,            // Redirect to root
        /~\//,               // Home directory access
    ];
    
    for (const pattern of dangerousPatterns) {
        if (pattern.test(trimmedCmd)) {
            throw new Error(`Padrão perigoso detectado no comando: ${pattern}`);
        }
    }
    
    // ✅ Bloqueia acesso a arquivos sensíveis
    for (const deniedPath of DENIED_PATHS) {
        if (trimmedCmd.includes(deniedPath)) {
            throw new Error(`Comando acessa caminho protegido: ${deniedPath}`);
        }
    }
    
    return trimmedCmd;
}

// ============================================
// CONTROLE DE RECURSOS
// ============================================

class ResourceManager {
    constructor() {
        this.cpuCores = os.cpus().length;
        this.allowedThreads = Math.max(1, Math.floor(this.cpuCores / 2));
        this.totalRam = os.totalmem();
        this.minFreeRam = this.totalRam * 0.2; // Reserva 20% de RAM
    }
    
    // ✅ Verifica recursos disponíveis
    checkResources() {
        const freeRam = os.freemem();
        const usedRamPercent = ((this.totalRam - freeRam) / this.totalRam) * 100;
        
        if (freeRam < this.minFreeRam) {
            throw new Error(`Memória insuficiente: ${usedRamPercent.toFixed(1)}% em uso. Mínimo necessário: 20% livre.`);
        }
        
        return {
            plataforma: os.platform(),
            ram_total_gb: (this.totalRam / 1024 / 1024 / 1024).toFixed(2),
            ram_livre_gb: (freeRam / 1024 / 1024 / 1024).toFixed(2),
            ram_uso_percent: usedRamPercent.toFixed(1),
            cpu_cores: this.cpuCores,
            threads_permitidas: this.allowedThreads,
            status: freeRam >= this.minFreeRam ? 'OK' : 'CRÍTICO'
        };
    }
    
    // ✅ Define prioridade baixa para não interferir no sistema
    setLowPriority() {
        try {
            os.setPriority(os.constants.priority.PRIORITY_BELOW_NORMAL);
            console.log(chalk.green('✓ Prioridade do processo definida como BAIXA'));
        } catch (e) {
            console.log(chalk.yellow('⚠ Não foi possível alterar prioridade do processo'));
        }
    }
}

const resourceManager = new ResourceManager();

// ============================================
// CONTROLADOR DE CUSTOS
// ============================================

class BudgetTracker {
    constructor() {
        this.inputTokens = 0;
        this.outputTokens = 0;
        this.iterations = 0;
        this.startTime = Date.now();
        
        // Preços estimados (ajustar conforme modelo)
        this.pricePer1MInput = 0.15;   // $0.15 por 1M tokens entrada
        this.pricePer1MOutput = 0.60;  // $0.60 por 1M tokens saída
    }
    
    recordUsage(inputTokens, outputTokens) {
        this.inputTokens += inputTokens;
        this.outputTokens += outputTokens;
        this.iterations++;
        
        // ✅ Verifica limites
        if (this.iterations >= CONFIG.MAX_ITERATIONS) {
            throw new Error(`Limite de iterações atingido: ${CONFIG.MAX_ITERATIONS}`);
        }
        
        const cost = this.getCurrentCost();
        if (cost >= CONFIG.MAX_COST_USD) {
            throw new Error(`Limite de custo atingido: $${cost.toFixed(4)} / $${CONFIG.MAX_COST_USD}`);
        }
    }
    
    getCurrentCost() {
        return (this.inputTokens / 1000000 * this.pricePer1MInput) +
               (this.outputTokens / 1000000 * this.pricePer1MOutput);
    }
    
    getSummary() {
        const elapsed = ((Date.now() - this.startTime) / 1000).toFixed(1);
        return {
            iterations: this.iterations,
            input_tokens: this.inputTokens,
            output_tokens: this.outputTokens,
            total_tokens: this.inputTokens + this.outputTokens,
            cost_usd: this.getCurrentCost().toFixed(4),
            elapsed_seconds: elapsed,
            max_iterations: CONFIG.MAX_ITERATIONS,
            max_cost_usd: CONFIG.MAX_COST_USD
        };
    }
}

const budgetTracker = new BudgetTracker();

// ============================================
// INTERFACE VISUAL MELHORADA
// ============================================

class Dashboard {
    static clear() {
        process.stdout.write('\x1Bc');
    }
    
    static header() {
        console.log(chalk.bgBlue.white.bold('\n === AGENTE AUTÔNOMO SEGURO v3.0 === \n'));
        console.log(chalk.cyan(` 🧠 Modelo: ${CONFIG.MODEL}`));
        console.log(chalk.cyan(` 📁 Workspace: ${CONFIG.WORKSPACE_DIR}`));
        console.log(chalk.cyan(` ⚙️ Max Iterações: ${CONFIG.MAX_ITERATIONS} | Max Custo: $${CONFIG.MAX_COST_USD}`));
        console.log(chalk.green(` 🔒 SANDBOX ATIVO | COMANDOS RESTRITOS | VALIDAÇÃO DE PATHS`));
        console.log(chalk.gray(' ==========================================================\n'));
    }
    
    static logSecurity(message) {
        console.log(chalk.red.bold(` 🔒 SEGURANÇA: `) + message);
        writeLog(`SEGURANÇA: ${message}`);
    }
    
    static logAction(action, details) {
        console.log(chalk.yellow(` ⚙️ AÇÃO: `) + chalk.bold(action));
        if (details) console.log(chalk.gray(`   └─ ${details}`));
        writeLog(`AÇÃO: ${action} - ${details || ''}`);
    }
    
    static logResult(result) {
        const preview = result.length > 200 ? result.substring(0, 200) + '...' : result;
        console.log(chalk.green(` ✅ RESULTADO: `) + chalk.gray(preview) + '\n');
        writeLog(`RESULTADO: ${result}`);
    }
    
    static logError(error) {
        console.log(chalk.red(` ❌ ERRO: `) + error + '\n');
        writeLog(`ERRO: ${error}`);
    }
    
    static showBudget() {
        const summary = budgetTracker.getSummary();
        console.log(chalk.magenta('\n 💰 ORÇAMENTO:'));
        console.log(chalk.gray(`   Iterações: ${summary.iterations}/${summary.max_iterations}`));
        console.log(chalk.gray(`   Tokens: ${summary.total_tokens.toLocaleString()}`));
        console.log(chalk.gray(`   Custo: $${summary.cost_usd} / $${summary.max_cost_usd}`));
        console.log(chalk.gray(`   Tempo: ${summary.elapsed_seconds}s\n`));
    }
}

// ============================================
// LOG ESTRUTURADO
// ============================================

const logStream = fs.createWriteStream(CONFIG.LOG_FILE, { flags: 'a' });

function writeLog(entry) {
    const timestamp = new Date().toISOString();
    logStream.write(`[${timestamp}] ${entry}\n`);
}

// ============================================
// SYSTEM PROMPT COM REGRAS DE SEGURANÇA
// ============================================

const SYSTEM_PROMPT = `Você é um Agente de Engenharia de Software Autônomo Nível 5.
Seu objetivo é resolver problemas complexos, gerenciar recursos e escrever código de produção no sistema local.
Seu diretório de trabalho base principal é: "${CONFIG.WORKSPACE_DIR}".

🚨 REGRAS OBRIGATÓRIAS DE SEGURANÇA:
1. NUNCA execute comandos destrutivos (rm -rf, format, del /f, etc.)
2. NUNCA acesse arquivos fora do workspace: ${CONFIG.WORKSPACE_DIR}
3. NUNCA leia credenciais (.env, .aws, .ssh, .kube, etc.)
4. SEMPRE valide comandos antes de executar
5. SEMPRE use caminhos absolutos dentro do workspace
6. SEMPRE inclua tratamento de erros em scripts

REGRAS OBRIGATÓRIAS DE PROGRAMAÇÃO:
1. ARQUIVOS DE ÁUDIO/RÁDIO: Use padrões .m3u ou .lst. Preserve metadados ID3 via 'mutagen'.
2. PADRÕES PYTHON: Use Google Style docs. Use raw strings (r'C:\\...') para caminhos Windows.
3. CÓDIGO COMPLETO: SEMPRE forneça o CÓDIGO COMPLETO. Proibido placeholders.
4. TRATAMENTO DE EXCEÇÕES: Inclua try-except obrigatórios. Registre erros em 'error.log'.
5. LINGUÍSTICA FORENSE: Use ferramenta 'analyzeTextForensics' para análise NLP.
6. TOM: Útil, claro e objetivo. Sem meta-comentários.

FERRAMENTAS (use EXCLUSIVAMENTE um bloco JSON por resposta):
{
  "tool": "nome_da_ferramenta",
  "parameters": { "chave": "valor" }
}

FERRAMENTAS DISPONÍVEIS:
1. listDir: { "path": "caminho" } - Lista diretório
2. readFile: { "path": "caminho" } - Lê arquivo
3. writeFile: { "path": "caminho", "content": "codigo" } - Escreve arquivo
4. runCommand: { "command": "comando" } - Executa comando SEGURO
5. checkResources: {} - Verifica recursos do sistema
6. analyzeTextForensics: { "path": "caminho", "analysis_type": "stylometry|ngrams" }
7. finishTask: { "summary": "resumo" } - FINALIZA TAREFA

⚠️ RESTRIÇÕES:
- runCommand: APENAS comandos de leitura permitidos (ls, cat, git status, etc.)
- Paths: APENAS dentro de ${CONFIG.WORKSPACE_DIR}
- Proibido: rm, sudo, curl | bash, wget | sh, chmod, chown
- Proibido: Acessar ~/.aws, ~/.ssh, ~/.kube, .env

Quando terminar, DEVE chamar "finishTask".`;

// ============================================
// MOTOR DO AGENTE SEGURO
// ============================================

async function executeToolCall(toolName, params) {
    Dashboard.logAction(`Executando ferramenta: ${toolName}`, JSON.stringify(params).substring(0, 100));
    
    try {
        switch (toolName) {
            case 'listDir': {
                const validatedPath = validatePath(params.path, 'read');
                const items = fs.readdirSync(validatedPath);
                return items.join('\n');
            }
            
            case 'readFile': {
                const validatedPath = validatePath(params.path, 'read');
                const content = fs.readFileSync(validatedPath, 'utf-8');
                // ✅ Limita tamanho da resposta
                return content.length > 50000 
                    ? content.substring(0, 50000) + '\n... [truncado]'
                    : content;
            }
            
            case 'writeFile': {
                const validatedPath = validatePath(params.path, 'write');
                fs.writeFileSync(validatedPath, params.content, 'utf-8');
                return `✓ Arquivo escrito: ${validatedPath} (${params.content.length} caracteres)`;
            }
            
            case 'runCommand': {
                const validatedCommand = validateCommand(params.command);
                return new Promise((resolve, reject) => {
                    exec(validatedCommand, {
                        timeout: CONFIG.COMMAND_TIMEOUT,
                        maxBuffer: 1024 * 1024,
                        cwd: CONFIG.WORKSPACE_DIR
                    }, (error, stdout, stderr) => {
                        if (error) {
                            Dashboard.logSecurity(`Comando falhou: ${error.message}`);
                            resolve(`Erro: ${error.message}`);
                        } else {
                            const output = (stdout || stderr).substring(0, 10000);
                            resolve(output || 'Comando executado com sucesso');
                        }
                    });
                });
            }
            
            case 'checkResources': {
                return JSON.stringify(resourceManager.checkResources(), null, 2);
            }
            
            case 'analyzeTextForensics': {
                const validatedPath = validatePath(params.path, 'read');
                // Implementar análise forense aqui
                return `Análise forense de ${validatedPath}: [implementação pendente]`;
            }
            
            case 'finishTask': {
                Dashboard.logAction('TAREFA FINALIZADA', params.summary);
                Dashboard.showBudget();
                return { finished: true, summary: params.summary };
            }
            
            default:
                throw new Error(`Ferramenta desconhecida: ${toolName}`);
        }
    } catch (error) {
        Dashboard.logSecurity(`BLOQUEADO: ${error.message}`);
        return `ERRO DE SEGURANÇA: ${error.message}`;
    }
}

// ============================================
// INICIALIZAÇÃO SEGURA
// ============================================

async function initializeAgent() {
    Dashboard.clear();
    Dashboard.header();
    
    // ✅ 1. Sanitiza ambiente
    sanitizeEnvironment();
    
    // ✅ 2. Verifica recursos
    try {
        const resources = resourceManager.checkResources();
        console.log(chalk.green(` ✓ Recursos OK: ${resources.ram_livre_gb}GB RAM livre`));
    } catch (error) {
        console.log(chalk.red(` ✗ ${error.message}`));
        process.exit(1);
    }
    
    // ✅ 3. Define prioridade baixa
    resourceManager.setLowPriority();
    
    // ✅ 4. Cria workspace se não existir
    if (!fs.existsSync(CONFIG.WORKSPACE_DIR)) {
        fs.mkdirpSync(CONFIG.WORKSPACE_DIR);
        console.log(chalk.green(` ✓ Workspace criado: ${CONFIG.WORKSPACE_DIR}`));
    }
    
    // ✅ 5. Verifica conexão com Ollama
    try {
        await axios.get('http://localhost:11434/api/tags', { timeout: 5000 });
        console.log(chalk.green(' ✓ Conexão com Ollama OK\n'));
    } catch (error) {
        console.log(chalk.red(' ✗ Ollama não está rodando. Inicie com: ollama serve'));
        process.exit(1);
    }
    
    writeLog(`AGENTE INICIADO - Workspace: ${CONFIG.WORKSPACE_DIR}`);
}

// ============================================
// TRATAMENTO DE INTERRUPÇÕES
// ============================================

process.on('SIGINT', async () => {
    console.log(chalk.bgRed.white.bold('\n\n[!] INTERRUPÇÃO DETECTADA (Ctrl+C)'));
    writeLog('INTERRUPÇÃO: Usuário interrompeu execução');
    
    const summary = budgetTracker.getSummary();
    console.log(chalk.yellow('\n📊 Resumo da Sessão:'));
    console.log(chalk.gray(`   Iterações: ${summary.iterations}`));
    console.log(chalk.gray(`   Tokens: ${summary.total_tokens}`));
    console.log(chalk.gray(`   Custo: $${summary.cost_usd}`));
    
    logStream.end();
    process.exit(0);
});

// ============================================
// LOOP PRINCIPAL DO AGENTE
// ============================================

async function runAgent(userGoal) {
    await initializeAgent();
    
    let history = [{ role: 'system', content: SYSTEM_PROMPT }];
    history.push({ role: 'user', content: userGoal });
    
    let iteration = 0;
    
    while (iteration < CONFIG.MAX_ITERATIONS) {
        iteration++;
        Dashboard.logAction(`Iteração ${iteration}/${CONFIG.MAX_ITERATIONS}`);
        
        try {
            // ✅ Envia requisição para Ollama
            const response = await axios.post(CONFIG.OLLAMA_URL, {
                model: CONFIG.MODEL,
                messages: history,
                stream: false,
                options: {
                    num_ctx: 8192,
                    temperature: 0.7,
                    top_p: 0.9
                }
            }, {
                timeout: CONFIG.HTTP_TIMEOUT,
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const assistantMessage = response.data.message;
            history.push({ role: 'assistant', content: assistantMessage.content });
            
            // ✅ Registra uso
            if (response.data.eval_count) {
                budgetTracker.recordUsage(
                    response.data.prompt_eval_count || 0,
                    response.data.eval_count || 0
                );
            }
            
            // ✅ Extrai tool calls
            const toolCalls = extractToolCalls(assistantMessage.content);
            
            if (toolCalls.length === 0) {
                // Sem tool calls - resposta final
                Dashboard.logResult(assistantMessage.content);
                Dashboard.showBudget();
                return assistantMessage.content;
            }
            
            // ✅ Executa tools
            for (const toolCall of toolCalls) {
                const result = await executeToolCall(toolCall.tool, toolCall.parameters);
                
                if (result && result.finished) {
                    Dashboard.showBudget();
                    return result.summary;
                }
                
                history.push({
                    role: 'user',
                    content: JSON.stringify({ tool_result: result })
                });
            }
            
        } catch (error) {
            Dashboard.logError(error.message);
            
            if (error.message.includes('Limite de') || error.message.includes('atingido')) {
                Dashboard.showBudget();
                return error.message;
            }
            
            // Recupera de erros
            history.push({
                role: 'user',
                content: `Erro: ${error.message}. Tente uma abordagem diferente.`
            });
        }
    }
    
    Dashboard.logError('Limite máximo de iterações atingido');
    Dashboard.showBudget();
    return 'Tarefa não concluída: limite de iterações excedido';
}

// ============================================
// EXTRAI TOOL CALLS DO TEXTO
// ============================================

function extractToolCalls(text) {
    const toolCalls = [];
    
    // ✅ Procura blocos JSON
    const jsonPattern = /\{[\s\S]*?"tool"[\s\S]*?"parameters"[\s\S]*?\}/g;
    const matches = text.match(jsonPattern) || [];
    
    for (const match of matches) {
        try {
            const parsed = JSON.parse(match);
            if (parsed.tool && parsed.parameters) {
                toolCalls.push(parsed);
            }
        } catch (e) {
            // Ignora JSON inválido
        }
    }
    
    return toolCalls;
}

// ============================================
// PONTO DE ENTRADA
// ============================================

async function main() {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.log(chalk.yellow('Uso: node agent.js "sua tarefa aqui"'));
        console.log(chalk.gray('Exemplo: node agent.js "Liste todos os arquivos Python do projeto"'));
        process.exit(0);
    }
    
    const userGoal = args.join(' ');
    console.log(chalk.blue.bold(`\n🎯 TAREFA: ${userGoal}\n`));
    
    try {
        const result = await runAgent(userGoal);
        console.log(chalk.green.bold('\n✓ TAREFA CONCLUÍDA:\n'));
        console.log(result);
    } catch (error) {
        console.log(chalk.red.bold('\n✗ ERRO FATAL:\n'));
        console.error(error);
    } finally {
        logStream.end();
    }
}

// ✅ Executa
main().catch(error => {
    console.error(chalk.red.bold('Erro fatal:'), error);
    process.exit(1);
});
