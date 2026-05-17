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

            positions: (data.positions || []).map((item) => {
                // /api/positions/ returns { value: <int>, label: <string>, code: <string> }
                // older endpoints may return { id, name } — handle both
                if (typeof item === "string") {
                    return { key: item, value: item, label: item };
                }
                const id = item.value ?? item.id;
                const name = item.label ?? item.name ?? item.title ?? String(id ?? "");
                return {
                    key: id,
                    value: id,   // integer position ID — sent to backend
                    label: name,
                    code: item.code ?? "",
                };
            }),
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