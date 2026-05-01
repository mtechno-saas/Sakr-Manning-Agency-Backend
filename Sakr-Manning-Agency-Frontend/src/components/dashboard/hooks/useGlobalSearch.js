// hooks/useGlobalSearch.js
// Global search logic across all data sources
// Returns categorized search results from all pages

import { useMemo } from "react";

/**
 * useGlobalSearch Hook
 *
 * Searches across ALL data sources in the application
 * Returns results grouped by category (CVs, Companies, Users, etc.)
 *
 * @param {string} query - Search query string
 * @param {object} allData - Object containing all data sources
 * @returns {object} Categorized search results
 *
 * @example
 * const { results, totalResults, hasResults } = useGlobalSearch(searchQuery, {
 *   cvs: cvData,
 *   companies: companyData,
 *   ships: shipData,
 *   users: userData,
 *   interviews: interviewData,
 *   documents: documentData,
 *   finance: financeData
 * });
 */
const useGlobalSearch = (query = "", allData = {}) => {
  const results = useMemo(() => {
    // Return empty if no query
    if (!query || query.trim().length === 0) {
      return {
        cvs: [],
        companies: [],
        ships: [],
        users: [],
        interviews: [],
        documents: [],
        finance: [],
      };
    }

    const searchTerm = query.toLowerCase().trim();

    // Helper function to check if value matches search term
    const matchesSearch = (value) => {
      if (value == null) return false;
      return String(value).toLowerCase().includes(searchTerm);
    };

    // Helper to search an object's fields
    const searchObject = (obj, fields) => {
      return fields.some((field) => matchesSearch(obj[field]));
    };

    // Search CVs
    const cvResults = (allData.cvs || []).filter((cv) =>
      searchObject(cv, [
        "name",
        "position",
        "experience",
        "submitted",
        "status",
      ])
    );

    // Search Companies
    const companyResults = (allData.companies || []).filter((company) =>
      searchObject(company, ["name", "type", "email", "status"])
    );

    // Search Ships
    const shipResults = (allData.ships || []).filter((ship) =>
      searchObject(ship, [
        "name",
        "imoNumber",
        "flag",
        "type",
        "company",
        "status",
      ])
    );

    // Search Users
    const userResults = (allData.users || []).filter((user) =>
      searchObject(user, ["name", "email", "role", "lastLogin", "status"])
    );

    // Search Interviews
    const interviewResults = (allData.interviews || []).filter((interview) =>
      searchObject(interview, [
        "candidateName",
        "position",
        "company",
        "date",
        "time",
        "type",
        "status",
      ])
    );

    // Search Documents
    const documentResults = (allData.documents || []).filter((doc) =>
      searchObject(doc, ["name", "position", "status", "generated", "signed"])
    );

    // Search Finance Records
    const financeResults = (allData.finance || []).filter((record) =>
      searchObject(record, ["user", "company", "startDate", "endDate"])
    );

    return {
      cvs: cvResults,
      companies: companyResults,
      ships: shipResults,
      users: userResults,
      interviews: interviewResults,
      documents: documentResults,
      finance: financeResults,
    };
  }, [query, allData]);

  // Calculate total results
  const totalResults = useMemo(() => {
    return Object.values(results).reduce((sum, arr) => sum + arr.length, 0);
  }, [results]);

  // Check if any results exist
  const hasResults = totalResults > 0;

  // Get results by category
  const getResultsByCategory = (category) => {
    return results[category] || [];
  };

  // Get category counts
  const categoryCounts = useMemo(() => {
    return {
      cvs: results.cvs.length,
      companies: results.companies.length,
      ships: results.ships.length,
      users: results.users.length,
      interviews: results.interviews.length,
      documents: results.documents.length,
      finance: results.finance.length,
    };
  }, [results]);

  return {
    results,
    totalResults,
    hasResults,
    categoryCounts,
    getResultsByCategory,
  };
};

export default useGlobalSearch;
