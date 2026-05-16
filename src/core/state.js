/**
 * PASA v47.1 - State Manager: Centralized Application State
 * Single source of truth for all UI state
 */
export const State = {
  view: 'monitor',
  comments: [],
  workers: [],
  profilerStream: [],
  kpis: { targets: 0, hate: 0, total: 0, resiliencia: 100 },
  currentFilter: 'all',
  searchTerm: '',
  isLoading: { comments: false, workers: false, profiler: false, kpis: false },
  error: null,
  pagination: { page: 1, limit: 20, hasMore: true },
  // Mantendo campos necessários para a UI atual
  sidebarCollapsed: false,
  rightSidebarCollapsed: false,
  selectedTarget: null
};

// State mutation functions (pure functions)
export const stateMutations = {
    setView: (state, view) => {
        state.view = view;
        // Update URL without reload
        if (view !== 'monitor') {
            window.history.pushState(null, '', `#${view}`);
        } else {
            window.history.pushState(null, '', window.location.pathname);
        }
    },
    
    setSidebarCollapsed: (state, collapsed) => {
        state.sidebarCollapsed = collapsed;
    },
    
    setRightSidebarCollapsed: (state, collapsed) => {
        state.rightSidebarCollapsed = collapsed;
    },
    
    setComments: (state, comments) => {
        state.comments = comments;
        state.isLoading.comments = false;
    },
    
    setWorkers: (state, workers) => {
        state.workers = workers;
        state.isLoading.workers = false;
    },
    
    setProfilerStream: (state, stream) => {
        state.profilerStream = stream;
        state.isLoading.profiler = false;
    },
    
    setKpis: (state, kpis) => {
        state.kpis = { ...state.kpis, ...kpis };
        state.isLoading.kpis = false;
    },
    
    setFilter: (state, filter) => {
        state.currentFilter = filter;
    },
    
    setSearchTerm: (state, term) => {
        state.searchTerm = term;
    },
    
    setSelectedTarget: (state, target) => {
        state.selectedTarget = target;
    },
    
    setLoading: (state, key, isLoading) => {
        state.isLoading[key] = isLoading;
    },
    
    setError: (state, error) => {
        state.error = error;
    },
    
    clearError: (state) => {
        state.error = null;
    },
    
    updatePagination: (state, { page, limit, hasMore }) => {
        state.pagination.page = page;
        state.pagination.limit = limit;
        state.pagination.hasMore = hasMore;
    }
};

// Computed selectors
export const selectors = {
    filteredComments: (state) => {
        let comments = state.comments;
        
        // Apply filter
        if (state.currentFilter === 'hate') {
            comments = comments.filter(c => c.is_hate === true);
        } else if (state.currentFilter === 'critical') {
            comments = comments.filter(c => c.is_hate === true && c.confianca_ia >= 0.8);
        }
        
        // Apply search
        if (state.searchTerm.trim() !== '') {
            const term = state.searchTerm.toLowerCase().trim();
            comments = comments.filter(c => 
                (c.texto_limpo || '').toLowerCase().includes(term) ||
                (c.autor_username || '').toLowerCase().includes(term)
            );
        }
        
        // Apply selected target
        if (state.selectedTarget) {
            comments = comments.filter(c => 
                String(c.candidato_id) === String(state.selectedTarget.username)
            );
        }
        
        return comments;
    },
    
    paginatedComments: (state) => {
        const comments = selectors.filteredComments(state);
        const start = (state.pagination.page - 1) * state.pagination.limit;
        const end = start + state.pagination.limit;
        return comments.slice(start, end);
    },
    
    hasMoreComments: (state) => {
        return selectors.filteredComments(state).length > 
               state.pagination.page * state.pagination.limit;
    }
};
