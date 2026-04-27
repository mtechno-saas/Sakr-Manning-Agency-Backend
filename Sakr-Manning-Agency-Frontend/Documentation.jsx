import React, { useState } from 'react';
import { Search, Filter, X, ChevronDown } from 'lucide-react';

const FilterSearchGuide = () => {
    const [activeTab, setActiveTab] = useState('overview');
    const [showExample, setShowExample] = useState('users');

    const tabs = [
        { id: 'overview', label: 'Overview' },
        { id: 'endpoints', label: 'Endpoints' },
        { id: 'examples', label: 'Code Examples' },
        { id: 'components', label: 'UI Components' }
    ];

    const filterEndpoints = {
        users: {
            endpoint: '/api/users/',
            altEndpoint: '/api/filter/',
            params: [
                { name: 'search', type: 'string', description: 'General search across fields' },
                { name: 'role', type: 'enum', values: ['admin', 'hr_manager', 'recruiter', 'employee'] },
                { name: 'nationality', type: 'string', description: 'Filter by nationality' },
                { name: 'user_status', type: 'enum', values: ['VECATION', 'ON_SITE', 'MEDICAL VECATION'] },
                { name: 'marital_status', type: 'enum', values: ['SINGLE', 'MARRIED'] },
                { name: 'email', type: 'string', description: 'Filter by email' },
                { name: 'first_name', type: 'string', description: 'Filter by first name' },
                { name: 'page', type: 'number', description: 'Page number for pagination' },
                { name: 'page_size', type: 'number', description: 'Items per page' }
            ]
        },
        companies: {
            endpoint: '/api/companies/',
            params: [
                { name: 'company_type', type: 'enum', values: ['ship_owner', 'ship_manager', 'crewing_agency', 'other'] },
                { name: 'status', type: 'enum', values: ['active', 'inactive', 'prospect'] },
                { name: 'country', type: 'string', description: 'Filter by country' },
                { name: 'page', type: 'number' },
                { name: 'page_size', type: 'number' }
            ]
        },
        interviews: {
            endpoint: '/api/interviews/interviews/',
            params: [
                { name: 'status', type: 'enum', values: ['scheduled', 'completed', 'cancelled', 'no_show', 'rescheduled'] },
                { name: 'interview_type', type: 'enum', values: ['in_person', 'video', 'phone'] },
                { name: 'candidate', type: 'number', description: 'User ID of candidate' },
                { name: 'page', type: 'number' },
                { name: 'page_size', type: 'number' }
            ]
        },
        cvSubmissions: {
            endpoint: '/api/cv-submissions/',
            params: [
                { name: 'status', type: 'enum', values: ['submitted', 'under_review', 'shortlisted', 'rejected', 'accepted'] },
                { name: 'user', type: 'number', description: 'User ID' },
                { name: 'company', type: 'number', description: 'Company ID' },
                { name: 'rating', type: 'number', description: 'Filter by rating (1-5)' },
                { name: 'page', type: 'number' },
                { name: 'page_size', type: 'number' }
            ]
        }
    };

    const codeExamples = {
        basicFetch: `// Basic filtering with fetch
const fetchUsers = async (filters) => {
  const queryParams = new URLSearchParams();
  
  // Add filters to query string
  Object.keys(filters).forEach(key => {
    if (filters[key]) {
      queryParams.append(key, filters[key]);
    }
  });
  
  const response = await fetch(
    \`http://localhost:8000/api/users/?\${queryParams}\`,
    {
      headers: {
        'Authorization': \`Bearer \${accessToken}\`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  return await response.json();
};

// Usage
const users = await fetchUsers({
  nationality: 'Egyptian',
  role: 'employee',
  user_status: 'ON_SITE',
  page: 1,
  page_size: 20
});`,

        reactHook: `// React custom hook for filtering
import { useState, useEffect } from 'react';

const useFilter = (endpoint, initialFilters = {}) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState(initialFilters);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 20,
    total: 0
  });

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const queryParams = new URLSearchParams({
        ...filters,
        page: pagination.page,
        page_size: pagination.pageSize
      });

      const response = await fetch(\`\${endpoint}?\${queryParams}\`, {
        headers: {
          Authorization: \`Bearer \${localStorage.getItem('access_token')}\`
        }
      });
      
      const result = await response.json();
      setData(result.results || result);
      setPagination(prev => ({
        ...prev,
        total: result.count || result.length
      }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filters, pagination.page, pagination.pageSize]);

  const updateFilters = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const clearFilters = () => {
    setFilters(initialFilters);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  return {
    data,
    loading,
    error,
    filters,
    pagination,
    updateFilters,
    clearFilters,
    refetch: fetchData
  };
};

// Usage in component
const UserList = () => {
  const { 
    data: users, 
    loading, 
    updateFilters, 
    clearFilters 
  } = useFilter('/api/users/', { role: 'employee' });

  return (
    <div>
      <button onClick={() => updateFilters({ nationality: 'Egyptian' })}>
        Filter Egyptian
      </button>
      <button onClick={clearFilters}>Clear</button>
      {loading ? <p>Loading...</p> : users.map(user => (
        <div key={user.id}>{user.first_name}</div>
      ))}
    </div>
  );
};`,

        aiSearch: `// AI-powered natural language search
const aiSearch = async (query, sessionId = null) => {
  const response = await fetch('http://localhost:8000/ai-agents/chat/', {
    method: 'POST',
    headers: {
      'Authorization': \`Bearer \${accessToken}\`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: query,
      session_id: sessionId
    })
  });
  
  return await response.json();
};

// Usage
const result = await aiSearch(
  'Find all masters available for assignment'
);

// Result includes:
// - response: Natural language answer
// - session_id: For continuing conversation
// - message_id: Unique message identifier`,

        urlBuilder: `// Utility function for building query URLs
const buildQueryUrl = (baseUrl, filters) => {
  const url = new URL(baseUrl, window.location.origin);
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      if (Array.isArray(value)) {
        value.forEach(v => url.searchParams.append(key, v));
      } else {
        url.searchParams.append(key, value);
      }
    }
  });
  
  return url.toString();
};

// Usage
const url = buildQueryUrl('http://localhost:8000/api/users/', {
  nationality: 'Egyptian',
  role: 'employee',
  user_status: 'ON_SITE',
  page: 1
});
// Result: http://localhost:8000/api/users/?nationality=Egyptian&role=employee&user_status=ON_SITE&page=1`,

        debounceSearch: `// Debounced search implementation
const useDebounce = (value, delay = 500) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
};

// Usage in search component
const SearchableList = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 500);

  useEffect(() => {
    if (debouncedSearch) {
      // Fetch with search term
      fetchUsers({ search: debouncedSearch });
    }
  }, [debouncedSearch]);

  return (
    <input
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
      placeholder="Search users..."
    />
  );
};`
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                        Filter & Search Implementation Guide
                    </h1>
                    <p className="text-gray-300">
                        Complete guide for implementing backend filtering and search in your frontend
                    </p>
                </div>

                {/* Tabs */}
                <div className="flex gap-2 mb-6 border-b border-gray-700">
                    {tabs.map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`px-6 py-3 font-medium transition-all ${activeTab === tab.id
                                    ? 'border-b-2 border-blue-400 text-blue-400'
                                    : 'text-gray-400 hover:text-gray-200'
                                }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Content */}
                <div className="bg-gray-800 rounded-lg p-6">
                    {activeTab === 'overview' && (
                        <div className="space-y-6">
                            <h2 className="text-2xl font-bold text-blue-400">Overview</h2>

                            <div className="bg-gray-900 p-6 rounded-lg">
                                <h3 className="text-xl font-semibold mb-4">Available Filter Mechanisms</h3>
                                <div className="grid md:grid-cols-2 gap-4">
                                    <div className="bg-gray-800 p-4 rounded">
                                        <div className="flex items-center gap-2 mb-2">
                                            <Filter className="text-green-400" size={20} />
                                            <h4 className="font-semibold">Query Parameter Filtering</h4>
                                        </div>
                                        <p className="text-sm text-gray-300">
                                            Standard REST API filtering using URL query parameters. Most endpoints support this.
                                        </p>
                                        <code className="block mt-2 text-xs bg-gray-900 p-2 rounded">
                                            GET /api/users/?nationality=Egyptian&role=employee
                                        </code>
                                    </div>

                                    <div className="bg-gray-800 p-4 rounded">
                                        <div className="flex items-center gap-2 mb-2">
                                            <Search className="text-blue-400" size={20} />
                                            <h4 className="font-semibold">Search Parameter</h4>
                                        </div>
                                        <p className="text-sm text-gray-300">
                                            General search across multiple fields using the 'search' parameter.
                                        </p>
                                        <code className="block mt-2 text-xs bg-gray-900 p-2 rounded">
                                            GET /api/users/?search=john
                                        </code>
                                    </div>

                                    <div className="bg-gray-800 p-4 rounded">
                                        <div className="flex items-center gap-2 mb-2">
                                            <Filter className="text-purple-400" size={20} />
                                            <h4 className="font-semibold">Dedicated Filter Endpoint</h4>
                                        </div>
                                        <p className="text-sm text-gray-300">
                                            Special endpoint for advanced filtering with django-filter.
                                        </p>
                                        <code className="block mt-2 text-xs bg-gray-900 p-2 rounded">
                                            GET /api/filter/?nationality=Egyptian&user_status=ON_SITE
                                        </code>
                                    </div>

                                    <div className="bg-gray-800 p-4 rounded">
                                        <div className="flex items-center gap-2 mb-2">
                                            <Search className="text-yellow-400" size={20} />
                                            <h4 className="font-semibold">AI-Powered Search</h4>
                                        </div>
                                        <p className="text-sm text-gray-300">
                                            Natural language queries using AI chat agent.
                                        </p>
                                        <code className="block mt-2 text-xs bg-gray-900 p-2 rounded">
                                            POST /ai-agents/chat/ {`{message: "Find masters"}`}
                                        </code>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-yellow-900/20 border border-yellow-700 p-4 rounded-lg">
                                <h3 className="font-semibold text-yellow-400 mb-2">Key Points</h3>
                                <ul className="space-y-2 text-sm text-gray-300">
                                    <li>• All authenticated endpoints require JWT token in Authorization header</li>
                                    <li>• Pagination is available via <code className="bg-gray-700 px-1">page</code> and <code className="bg-gray-700 px-1">page_size</code> parameters</li>
                                    <li>• Filters can be combined: <code className="bg-gray-700 px-1">?role=employee&nationality=Egyptian&page=1</code></li>
                                    <li>• Empty/null values should be excluded from query parameters</li>
                                    <li>• Use URLSearchParams or similar for proper query string encoding</li>
                                </ul>
                            </div>
                        </div>
                    )}

                    {activeTab === 'endpoints' && (
                        <div className="space-y-6">
                            <h2 className="text-2xl font-bold text-blue-400">Filter Endpoints</h2>

                            <div className="flex gap-2 mb-4 flex-wrap">
                                {Object.keys(filterEndpoints).map(key => (
                                    <button
                                        key={key}
                                        onClick={() => setShowExample(key)}
                                        className={`px-4 py-2 rounded ${showExample === key
                                                ? 'bg-blue-600 text-white'
                                                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                            }`}
                                    >
                                        {key.charAt(0).toUpperCase() + key.slice(1)}
                                    </button>
                                ))}
                            </div>

                            <div className="bg-gray-900 p-6 rounded-lg">
                                <div className="mb-4">
                                    <h3 className="text-xl font-semibold mb-2">
                                        {filterEndpoints[showExample].endpoint}
                                    </h3>
                                    {filterEndpoints[showExample].altEndpoint && (
                                        <p className="text-sm text-gray-400">
                                            Alternative: {filterEndpoints[showExample].altEndpoint}
                                        </p>
                                    )}
                                </div>

                                <div className="space-y-3">
                                    <h4 className="font-semibold text-gray-300">Available Parameters:</h4>
                                    {filterEndpoints[showExample].params.map((param, idx) => (
                                        <div key={idx} className="bg-gray-800 p-3 rounded">
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <code className="text-green-400">{param.name}</code>
                                                    <span className="text-gray-500 ml-2">({param.type})</span>
                                                </div>
                                            </div>
                                            {param.description && (
                                                <p className="text-sm text-gray-400 mt-1">{param.description}</p>
                                            )}
                                            {param.values && (
                                                <div className="mt-2">
                                                    <span className="text-xs text-gray-500">Values: </span>
                                                    <div className="flex flex-wrap gap-1 mt-1">
                                                        {param.values.map((val, i) => (
                                                            <span key={i} className="text-xs bg-gray-700 px-2 py-1 rounded">
                                                                {val}
                                                            </span>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>

                                <div className="mt-6 p-4 bg-gray-800 rounded">
                                    <h4 className="font-semibold mb-2">Example Request:</h4>
                                    <code className="text-sm text-green-400 break-all">
                                        GET {filterEndpoints[showExample].endpoint}?
                                        {filterEndpoints[showExample].params.slice(0, 3).map((p, i) =>
                                            `${i > 0 ? '&' : ''}${p.name}=${p.values ? p.values[0] : 'value'}`
                                        ).join('')}
                                    </code>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'examples' && (
                        <div className="space-y-6">
                            <h2 className="text-2xl font-bold text-blue-400">Code Examples</h2>

                            <div className="space-y-4">
                                {Object.entries(codeExamples).map(([key, code]) => (
                                    <details key={key} className="bg-gray-900 rounded-lg overflow-hidden">
                                        <summary className="px-6 py-4 cursor-pointer hover:bg-gray-800 font-semibold flex items-center justify-between">
                                            {key.replace(/([A-Z])/g, ' $1').trim()}
                                            <ChevronDown size={20} />
                                        </summary>
                                        <pre className="p-6 overflow-x-auto text-sm bg-gray-950">
                                            <code className="text-green-400">{code}</code>
                                        </pre>
                                    </details>
                                ))}
                            </div>
                        </div>
                    )}

                    {activeTab === 'components' && (
                        <div className="space-y-6">
                            <h2 className="text-2xl font-bold text-blue-400">Reusable UI Components</h2>

                            <div className="bg-gray-900 p-6 rounded-lg">
                                <h3 className="text-xl font-semibold mb-4">Filter Component Example</h3>
                                <pre className="p-4 bg-gray-950 rounded overflow-x-auto text-sm">
                                    <code className="text-green-400">{`const FilterPanel = ({ onFilterChange, filters }) => {
  const [localFilters, setLocalFilters] = useState(filters);

  const handleChange = (key, value) => {
    const updated = { ...localFilters, [key]: value };
    setLocalFilters(updated);
  };

  const applyFilters = () => {
    onFilterChange(localFilters);
  };

  const clearFilters = () => {
    setLocalFilters({});
    onFilterChange({});
  };

  return (
    <div className="bg-gray-800 p-4 rounded-lg space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Filters</h3>
        <button onClick={clearFilters} className="text-sm text-blue-400">
          Clear All
        </button>
      </div>

      <div className="space-y-3">
        <div>
          <label className="block text-sm mb-1">Nationality</label>
          <input
            type="text"
            value={localFilters.nationality || ''}
            onChange={(e) => handleChange('nationality', e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 rounded"
          />
        </div>

        <div>
          <label className="block text-sm mb-1">Role</label>
          <select
            value={localFilters.role || ''}
            onChange={(e) => handleChange('role', e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 rounded"
          >
            <option value="">All</option>
            <option value="admin">Admin</option>
            <option value="employee">Employee</option>
            <option value="hr_manager">HR Manager</option>
            <option value="recruiter">Recruiter</option>
          </select>
        </div>

        <div>
          <label className="block text-sm mb-1">Status</label>
          <select
            value={localFilters.user_status || ''}
            onChange={(e) => handleChange('user_status', e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 rounded"
          >
            <option value="">All</option>
            <option value="VECATION">Vacation</option>
            <option value="ON_SITE">On Site</option>
            <option value="MEDICAL VECATION">Medical Vacation</option>
          </select>
        </div>
      </div>

      <button
        onClick={applyFilters}
        className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded"
      >
        Apply Filters
      </button>
    </div>
  );
};`}</code>
                                </pre>
                            </div>

                            <div className="bg-gray-900 p-6 rounded-lg">
                                <h3 className="text-xl font-semibold mb-4">Search Bar Component</h3>
                                <pre className="p-4 bg-gray-950 rounded overflow-x-auto text-sm">
                                    <code className="text-green-400">{`const SearchBar = ({ onSearch, placeholder = "Search..." }) => {
  const [query, setQuery] = useState('');
  const [debounceTimeout, setDebounceTimeout] = useState(null);

  const handleSearch = (value) => {
    setQuery(value);
    
    // Debounce search
    if (debounceTimeout) clearTimeout(debounceTimeout);
    
    const timeout = setTimeout(() => {
      onSearch(value);
    }, 500);
    
    setDebounceTimeout(timeout);
  };

  return (
    <div className="relative">
      <Search 
        className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" 
        size={20} 
      />
      <input
        type="text"
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
        placeholder={placeholder}
        className="w-full pl-10 pr-10 py-2 bg-gray-700 rounded-lg"
      />
      {query && (
        <button
          onClick={() => {
            setQuery('');
            onSearch('');
          }}
          className="absolute right-3 top-1/2 transform -translate-y-1/2"
        >
          <X className="text-gray-400 hover:text-white" size={20} />
        </button>
      )}
    </div>
  );
};`}</code>
                                </pre>
                            </div>
                        </div>
                    )}
                </div>

                {/* Quick Reference */}
                <div className="mt-8 bg-gradient-to-r from-blue-900/50 to-purple-900/50 p-6 rounded-lg border border-blue-700">
                    <h3 className="text-xl font-bold mb-4">Quick Reference</h3>
                    <div className="grid md:grid-cols-2 gap-4 text-sm">
                        <div>
                            <h4 className="font-semibold text-blue-400 mb-2">Authentication</h4>
                            <code className="block bg-gray-900 p-2 rounded">
                                Authorization: Bearer {`<access_token>`}
                            </code>
                        </div>
                        <div>
                            <h4 className="font-semibold text-blue-400 mb-2">Base URL</h4>
                            <code className="block bg-gray-900 p-2 rounded">
                                http://localhost:8000/api/
                            </code>
                        </div>
                        <div>
                            <h4 className="font-semibold text-blue-400 mb-2">Pagination</h4>
                            <code className="block bg-gray-900 p-2 rounded">
                                ?page=1&page_size=20
                            </code>
                        </div>
                        <div>
                            <h4 className="font-semibold text-blue-400 mb-2">Multiple Filters</h4>
                            <code className="block bg-gray-900 p-2 rounded">
                                ?filter1=value1&filter2=value2
                            </code>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FilterSearchGuide;