// contexts/ReferenceDataContext.jsx
import React, { createContext, useContext, useMemo } from "react";

const ReferenceDataContext = createContext(null);

/**
 * Provider for reference data (flags, vessel types, certificates, etc.)
 * Memoizes transformed options to prevent unnecessary re-renders
 */
export const ReferenceDataProvider = ({ children, data, isLoading }) => {
    const transformedData = useMemo(() => {
        if (!data) return null;
        return {
            // Original data
            raw: data,
            isLoading,

            // Transformed for Select components
            flags: (data.flags || []).map((item) => ({
                key: item.id,
                value: item.code || item.id,
                label: item.name,
            })),

            vesselTypes: (data.vesselTypes || []).map((item) => ({
                key: item.id,
                value: item.code || item.id,
                label: item.name,
            })),

            certificates: (data.certificates || []).map((item) => ({
                key: item.id,
                value: item.code || item.id,
                label: item.name,
            })),

            ranks: (data.ranks || []).map((item) => ({
                key: item.id,
                value: item.name || item.id,
                label: item.name,
            })),

            companies: (data.companies || []).map((item) => ({
                key: item.id,
                value: item.id,
                label: item.name,
            })),

            positions: (data.positions || []).map((item) => ({
                key: item.id,
                value: typeof item === "string" ? item : (item.id ?? item.value ?? item.name),
                label: typeof item === "string" ? item : (item.name ?? item.label ?? item.title),
            })),
        };
    }, [data, isLoading]);

    return (
        <ReferenceDataContext.Provider value={transformedData}>
            {children}
        </ReferenceDataContext.Provider>
    );
};

/**
 * Hook to access reference data
 * Returns null if context not available
 */
export const useReferenceDataContext = () => {
    const context = useContext(ReferenceDataContext);

    if (context === undefined) {
        throw new Error(
            "useReferenceDataContext must be used within ReferenceDataProvider"
        );
    }

    return context;
};

/**
 * HOC to inject reference data as props
 */
export const withReferenceData = (Component) => {
    return (props) => {
        const referenceData = useReferenceDataContext();
        return <Component {...props} referenceData={referenceData} />;
    };
};