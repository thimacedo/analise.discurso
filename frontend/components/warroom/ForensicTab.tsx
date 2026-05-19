'use client';
import { Card } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

export default function ForensicTab() {
  // Placeholder para dados reais do Supabase via React Query
  const comments = [
    { id: 1, text: "Exemplo de comentário ódio", category: "RACISMO", risk: "CRÍTICO" },
  ];

  return (
    <Card className="p-4 bg-black/50 border-tactical-accent">
      <h2 className="text-xl font-bold mb-4 text-tactical-accent">Análise Forense (Dados Reais)</h2>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Comentário</TableHead>
            <TableHead>Categoria</TableHead>
            <TableHead>Risco</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {comments.map((c) => (
            <TableRow key={c.id}>
              <TableCell>{c.text}</TableCell>
              <TableCell><Badge>{c.category}</Badge></TableCell>
              <TableCell><Badge variant="destructive">{c.risk}</Badge></TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
}
