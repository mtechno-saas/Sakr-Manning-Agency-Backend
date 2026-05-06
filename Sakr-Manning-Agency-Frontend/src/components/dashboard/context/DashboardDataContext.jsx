import React, { createContext, useContext, useState, useCallback, useRef, useEffect, useMemo } from "react";
import { usersApi, ranksApi, certificatesApi } from "../../../services/Dashboard/usersApi";
import { companiesApi } from "../../../services/Dashboard/companiesApi";
import { shipsApi, coreApi } from "../../../services/Dashboard/shipsApi";

/**
 * DashboardDataContext
 * 
 * Centralized cache for shared reference data across dashboard pages.
 * Prevents redundant API calls when navigating between pages.
 * 
 * Static Reference Data (preloaded on mount):
 * - Ranks
 * - Certificates
 * - Flags
 * - Vessel Types
 * 
 * Entity Data (cached on-demand):
 * - Companies (with batch fetch support)
 * - Ships by Company (cached per company)
 * - Company map (for O(1) lookups)
 * 
 * Search Functions (for TypeaheadInput):
 * - searchUsers (API call, not preloaded)
 * - searchCompanies (API call, not preloaded)
 */

const DashboardDataContext = createContext(null);

// Cache expiry time (15 minutes)
const CACHE_EXPIRY = 15 * 60 * 1000;

export function DashboardDataProvider({ children }) {
    // Static reference data caches
    const [ranks, setRanks] = useState([]);
    const [certificates, setCertificates] = useState([]);
    const [flags, setFlags] = useState([]);
    const [vesselTypes, setVesselTypes] = useState([]);

    // Entity data caches
    const [companies, setCompanies] = useState([]);
    const [users, setUsers] = useState([]);
    const [companyMap, setCompanyMap] = useState({});
    const [ships, setShips] = useState([]);
    const [shipsByCompany, setShipsByCompany] = useState({}); // { companyId: ships[] }

    // Loading states
    const [loadingCompanies, setLoadingCompanies] = useState(false);
    const [loadingUsers, setLoadingUsers] = useState(false);
    const [loadingRanks, setLoadingRanks] = useState(false);
    const [loadingFlags, setLoadingFlags] = useState(false);
    const [loadingVesselTypes, setLoadingVesselTypes] = useState(false);
    const [loadingCertificates, setLoadingCertificates] = useState(false);
    const [loadingShips, setLoadingShips] = useState(false);

    // Cache timestamps
    const cacheTimestamps = useRef({
        companies: 0,
        users: 0,
        ranks: 0,
        flags: 0,
        vesselTypes: 0,
        certificates: 0,
        ships: 0,
    });

    /**
     * Check if cache is still valid
     */
    const isCacheValid = useCallback((key) => {
        const timestamp = cacheTimestamps.current[key];
        return timestamp && (Date.now() - timestamp) < CACHE_EXPIRY;
    }, []);

    /**
     * Fetch companies (with caching)
     */
    const fetchCompanies = useCallback(async (force = false) => {
        if (!force && isCacheValid("companies") && companies.length > 0) {
            return companies;
        }

        setLoadingCompanies(true);
        try {
            const response = await companiesApi.getCompanies({ page_size: 1000 });
            const data = response.companies || [];
            setCompanies(data);
            cacheTimestamps.current.companies = Date.now();

            // Also populate company map
            const map = {};
            data.forEach(c => {
                map[c.id] = c;
            });
            setCompanyMap(prev => ({ ...prev, ...map }));

            return data;
        } catch (error) {
            console.error("Failed to fetch companies:", error);
            return [];
        } finally {
            setLoadingCompanies(false);
        }
    }, [companies, isCacheValid]);

    /**
     * Fetch users (with caching)
     */
    const fetchUsers = useCallback(async (force = false) => {
        if (!force && isCacheValid("users") && users.length > 0) {
            return users;
        }

        setLoadingUsers(true);
        try {
            const response = await usersApi.getUsers({ page_size: 1000 });
            const data = response.users || [];
            setUsers(data);
            cacheTimestamps.current.users = Date.now();
            return data;
        } catch (error) {
            console.error("Failed to fetch users:", error);
            return [];
        } finally {
            setLoadingUsers(false);
        }
    }, [users, isCacheValid]);

    /**
     * Fetch ranks (with caching)
     */
    const fetchRanks = useCallback(async (force = false) => {
        if (!force && isCacheValid("ranks") && ranks.length > 0) {
            return ranks;
        }

        setLoadingRanks(true);
        try {
            const data = await ranksApi.getRanks();
            setRanks(data);
            cacheTimestamps.current.ranks = Date.now();
            return data;
        } catch (error) {
            console.error("Failed to fetch ranks:", error);
            return [];
        } finally {
            setLoadingRanks(false);
        }
    }, [ranks, isCacheValid]);

    /**
     * Fetch flags (with caching, fetches ALL)
     */
    const fetchFlags = useCallback(async (force = false) => {
        if (!force && isCacheValid("flags") && flags.length > 0) {
            return flags;
        }

        setLoadingFlags(true);
        try {
            const data = await coreApi.getAllFlags();
            setFlags(data);
            cacheTimestamps.current.flags = Date.now();
            return data;
        } catch (error) {
            console.error("Failed to fetch flags:", error);
            return [];
        } finally {
            setLoadingFlags(false);
        }
    }, [flags, isCacheValid]);

    /**
     * Fetch vessel types (with caching)
     */
    const fetchVesselTypes = useCallback(async (force = false) => {
        if (!force && isCacheValid("vesselTypes") && vesselTypes.length > 0) {
            return vesselTypes;
        }

        setLoadingVesselTypes(true);
        try {
            const data = await coreApi.getVesselTypes();
            setVesselTypes(data);
            cacheTimestamps.current.vesselTypes = Date.now();
            return data;
        } catch (error) {
            console.error("Failed to fetch vessel types:", error);
            return [];
        } finally {
            setLoadingVesselTypes(false);
        }
    }, [vesselTypes, isCacheValid]);

    /**
     * Fetch certificates (with caching)
     */
    const fetchCertificates = useCallback(async (force = false) => {
        if (!force && isCacheValid("certificates") && certificates.length > 0) {
            return certificates;
        }

        setLoadingCertificates(true);
        try {
            const data = await certificatesApi.getCertificates();
            setCertificates(data);
            cacheTimestamps.current.certificates = Date.now();
            return data;
        } catch (error) {
            console.error("Failed to fetch certificates:", error);
            return [];
        } finally {
            setLoadingCertificates(false);
        }
    }, [certificates, isCacheValid]);

    /**
     * Fetch all ships (with caching)
     * Lazy-loaded when first needed
     */
    const fetchShips = useCallback(async (force = false) => {
        if (!force && isCacheValid("ships") && ships.length > 0) {
            return ships;
        }

        setLoadingShips(true);
        try {
            const response = await shipsApi.getShips({ page_size: 1000 });
            const data = response.ships || [];
            setShips(data);
            cacheTimestamps.current.ships = Date.now();
            return data;
        } catch (error) {
            console.error("Failed to fetch ships:", error);
            return [];
        } finally {
            setLoadingShips(false);
        }
    }, [ships, isCacheValid]);

    /**
     * Fetch ships by company (cached per company)
     * @param {number} companyId - Company ID
     * @param {boolean} force - Force refresh even if cached
     * @returns {Promise<Array>} Ships for the company
     */
    const fetchShipsByCompany = useCallback(async (companyId, force = false) => {
        if (!companyId) return [];

        // Return cached if valid and not forced
        if (!force && shipsByCompany[companyId] && shipsByCompany[companyId].length > 0) {
            return shipsByCompany[companyId];
        }

        try {
            // BE supports filtering ships by company
            const response = await shipsApi.getShips({ company: companyId, page_size: 1000 });
            const filteredShips = response.ships || [];

            setShipsByCompany(prev => ({
                ...prev,
                [companyId]: filteredShips
            }));

            return filteredShips;
        } catch (error) {
            console.error("Failed to fetch ships by company:", error);
            return [];
        }
    }, [shipsByCompany]);

    /**
     * Batch fetch companies by IDs and update cache
     */
    const fetchCompaniesByIds = useCallback(async (ids) => {
        const missingIds = ids.filter(id => id && !companyMap[id]);

        if (missingIds.length === 0) {
            // All already cached
            const result = {};
            ids.forEach(id => {
                if (id && companyMap[id]) {
                    result[id] = companyMap[id];
                }
            });
            return result;
        }

        try {
            const newData = await companiesApi.getCompaniesByIds(missingIds);
            setCompanyMap(prev => ({ ...prev, ...newData }));

            // Return combined result
            const result = { ...companyMap, ...newData };
            return result;
        } catch (error) {
            console.error("Failed to batch fetch companies:", error);
            return companyMap;
        }
    }, [companyMap]);

    /**
     * Get company name by ID (sync, uses cache)
     */
    const getCompanyName = useCallback((id) => {
        if (!id) return "Unknown Company";
        const company = companyMap[id];
        return company?.company_name || company?.name || "Unknown Company";
    }, [companyMap]);

    /**
     * Search users (for TypeaheadInput)
     */
    const searchUsers = useCallback(async (query, options = {}) => {
        return usersApi.searchUsers({
            search: query,
            role: options.role,
            limit: options.limit || 20,
        });
    }, []);

    /**
     * Search companies (for TypeaheadInput)
     */
    const searchCompanies = useCallback(async (query, options = {}) => {
        return companiesApi.searchCompanies({
            search: query,
            limit: options.limit || 20,
        });
    }, []);

    /**
     * Preload static reference data on mount
     */
    useEffect(() => {
        // Preload all static reference data when dashboard loads
        fetchCompanies();
        fetchUsers();
        fetchRanks();
        fetchFlags();
        fetchVesselTypes();
        fetchCertificates();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    /**
     * Pre-transformed options for Select components
     * Memoized to prevent unnecessary re-renders
     */
    const referenceOptions = useMemo(() => ({
        ranks: ranks.map(r => ({
            value: r.id,
            label: r.code ? `${r.code} - ${r.name}` : r.name
        })),
        certificates: certificates.map(c => ({
            value: c.id,
            label: c.code ? `${c.code} - ${c.name}` : c.name
        })),
        flags: flags.map(f => ({
            value: f.id,
            label: f.name
        })),
        vesselTypes: vesselTypes.map(v => ({
            value: v.id,
            label: v.name
        })),
        companies: companies.map(c => ({
            value: c.id,
            label: c.company_name || c.name || "Unknown Company"
        })),
        users: users.map(u => ({
            value: u.id,
            label: `${u.first_name || ''} ${u.middle_name || ''} ${u.last_name || ''}`.trim() || u.email
        })),
    }), [ranks, certificates, flags, vesselTypes, companies, users]);

    const value = {
        // Static Reference Data
        ranks,
        certificates,
        flags,
        vesselTypes,

        // Entity Data
        companies,
        users,
        companyMap,
        ships,
        shipsByCompany,

        // Pre-transformed options for forms
        referenceOptions,

        // Loading states
        loadingCompanies,
        loadingUsers,
        loadingRanks,
        loadingFlags,
        loadingVesselTypes,
        loadingCertificates,
        loadingShips,

        // Fetch methods - Static data
        fetchRanks,
        fetchCertificates,
        fetchFlags,
        fetchVesselTypes,
        fetchShips,

        // Fetch methods - Entity data
        fetchCompanies,
        fetchUsers,
        fetchCompaniesByIds,
        fetchShipsByCompany,

        // Utility methods
        getCompanyName,

        // TypeaheadInput search functions (for large datasets)
        searchUsers,
        searchCompanies,
    };

    return (
        <DashboardDataContext.Provider value={value}>
            {children}
        </DashboardDataContext.Provider>
    );
}

/**
 * Hook to access dashboard data context
 */
export function useDashboardData() {
    const context = useContext(DashboardDataContext);
    if (!context) {
        throw new Error("useDashboardData must be used within DashboardDataProvider");
    }
    return context;
}

export default DashboardDataContext;
