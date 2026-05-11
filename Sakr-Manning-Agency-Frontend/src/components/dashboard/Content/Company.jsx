/* eslint-disable no-unused-vars */

// Content/Company.jsx - COMPLETE with All Features from CV.jsx
import React, { useState, useEffect, useMemo, useCallback } from "react";
import { RefinedDataTable } from "../Components/Data/RefinedDataTable";
import { ExpandableDataTable } from "../Components/Data/ExpandableDataTable";
import Pagination from "../../common/Pagination";
import { StatisticsCard } from "../Components/Cards/StatisticsCards";
import { ASSETS } from "../../../utils/constants";
import { COLORS } from "../Constants";

import {
  generateAllPageStyles,
  getMainContainerStyles,
  getPageTitleStyles,
  getRowBetweenStyles,
} from "../Styles/cssClasses";
import { exportToExcel, exportToJSON } from "../../../utils/exportHelpers";

import Button from "../Components/Common/Button";
import EnhancedFilterModel from "../Components/Common/EnhancedFilterModel";
import SavedFilters from "../Components/Common/SavedFilters";
import ConfirmDialog from "../Components/Common/ConfirmDialog";

import CompanyFormModal from "../Components/Modal/CompanyFormModal";
import ShipFormModal from "../Components/Modal/ShipFormModal";
import JobOrderFormModal from "../Components/Modal/JobOrderFormModal";
import { CompanyViewModal, ShipViewModal } from "../Components/Modal/ViewModal";

import useTableFilters from "../hooks/useTableFilters";
import useNotification from "../hooks/useNotification";
import usePermissions from "../../../hooks/dashboard/usePermissions";

import useCompanies from "../../../hooks/dashboard/useCompanies";
import useShips from "../../../hooks/dashboard/useShips";
import useRanks from "../../../hooks/dashboard/useRanks";
import { coreApi } from "../../../services/Dashboard/shipsApi";

// Modals
import RankFormModal from "../Components/Modal/RankFormModal";
import CrewManagementModal from "../Components/Modal/CrewManagementModal";
import JobOrderManagementModal from "../Components/Modal/JobOrderManagementModal";
import useJobOrders from "../../../hooks/dashboard/useJobOrders";
import { useDashboardData } from "../context/DashboardDataContext";

export function CompanyManagement({ scale = 1, isMobile = false }) {
  const { notify } = useNotification();
  const { canCreate, canEdit, canDelete } = usePermissions();

  const {
    companies: backendCompanies,
    loading: companiesLoading,
    fetchCompanies,
    createCompany,
    updateCompany,
    deleteCompany,
    fetchCompanyStats,
    pagination: companyPagination,
  } = useCompanies();

  const { flags, vesselTypes, referenceOptions } = useDashboardData();

  const {
    ships: backendShips,
    loading: shipsLoading,
    fetchShips,
    createShip,
    updateShip,
    deleteShip,
    assignUser,
    unassignUser,
    pagination: shipPagination,
  } = useShips();

  const {
    jobOrders: backendJobOrders,
    loading: jobOrdersLoading,
    fetchJobOrders,
    createJobOrder,
    updateJobOrder,
    deleteJobOrder,
    pagination: jobOrderPagination,
  } = useJobOrders();

  const {
    ranks: backendRanks,
    loading: ranksLoading,
    fetchRanks,
    createRank,
    updateRank,
    deleteRank,
  } = useRanks();

  // Local state
  const [showCompanyModal, setShowCompanyModal] = useState(false);
  const [showShipModal, setShowShipModal] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [selectedShip, setSelectedShip] = useState(null);

  // View modals state
  const [showCompanyViewModal, setShowCompanyViewModal] = useState(false);
  const [viewingCompany, setViewingCompany] = useState(null);
  const [showShipViewModal, setShowShipViewModal] = useState(false);
  const [viewingShip, setViewingShip] = useState(null);

  // Job Orders filter state
  const [jobOrderFilters, setJobOrderFilters] = useState({
    company: "",
    ship: "",
    status: "",
    reference_number: "",
    request_date_from: "",
    request_date_to: ""
  });
  const [activeJobOrderFilters, setActiveJobOrderFilters] = useState({
    company: "",
    ship: "",
    status: "",
    reference_number: "",
    request_date_from: "",
    request_date_to: ""
  });
  const [showJobOrderFilterModal, setShowJobOrderFilterModal] = useState(false);

  // Ranks modal state
  const [showRankModal, setShowRankModal] = useState(false);
  const [selectedRank, setSelectedRank] = useState(null);

  // Crew management modal
  const [showCrewModal, setShowCrewModal] = useState(false);
  const [targetShipForCrew, setTargetShipForCrew] = useState(null);

  // Job Order management modal
  const [showJobOrderModal, setShowJobOrderModal] = useState(false);
  const [targetCompanyForJobOrder, setTargetCompanyForJobOrder] = useState(null);

  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [itemToDelete, setItemToDelete] = useState(null);
  const [deleteType, setDeleteType] = useState(null); // 'company', 'ship', 'job_order', 'rank'

  const [companyStats, setCompanyStats] = useState(null);

  // Filter state for Companies
  const [showCompanyFilterModal, setShowCompanyFilterModal] = useState(false);
  const [companyFilters, setCompanyFilters] = useState({
    name: "",
    status: "",
    company_type: "",
  });
  const [activeCompanyFilters, setActiveCompanyFilters] = useState({
    name: "",
    status: "",
    company_type: "",
  });

  // Filter state for Ships
  const [showShipFilterModal, setShowShipFilterModal] = useState(false);
  const [shipFilters, setShipFilters] = useState({
    name: "",
    imo_number: "",
    company: "",
    status: "",
    vessel_type: "",
  });
  const [activeShipFilters, setActiveShipFilters] = useState({
    name: "",
    imo_number: "",
    company: "",
    status: "",
    vessel_type: "",
  });

  // ✅ NEW: Saved filter presets for both companies and ships
  const [savedCompanyPresets, setSavedCompanyPresets] = useState([]);
  const [savedShipPresets, setSavedShipPresets] = useState([]);

  // Load data on mount
  useEffect(() => {
    fetchCompanies();
    fetchShips();
    fetchJobOrders();
    // fetchRanks();
  }, []);

  // Load company statistics
  const loadCompanyStats = useCallback(async () => {
    const result = await fetchCompanyStats();
    // console.log("company stats : ", result);
    if (result.success) {
      setCompanyStats(result.data);
    }
  }, [fetchCompanyStats]);

  // Transform backend companies to match UI format
  const companyData = useMemo(() => {
    return backendCompanies.map((company) => ({
      id: company.id,
      name: company.company_name,
      companyFlag: company.company_flag_name || "No Flag",
      type: company.company_type_name || "No Type",
      email: company.contact_email || "N/A",
      website: company.website || "-",
      createdAt: company.created_at || "N/A",
      hourRate: company.hourly_rate || 0,
      openPositions: company.open_positions || 0,
      status: company.status || "Active",
      avatar: ASSETS.LOGO,
      _original: company,
    }));
  }, [backendCompanies]);

  // Transform backend ships to match UI format
  const shipData = useMemo(() => {
    // console.log("the ships Company ID : ", backendShips[0]?.company);
    // console.log(
    //   "the maaped company : ",
    //   backendCompanies[backendShips[0]?.company]
    // );
    // console.log("the ship data beore mapping : ", backendShips);
    return backendShips.map((ship) => {
      // console.log("the flags data : ", flags);
      // console.log("the vessel types : ", vesselTypes);
      const associatedCompany = backendCompanies.find(
        (company) => company.id === ship.company
      );
      const associatedFlags = flags.find((flag) => {
        // console.log("the flag data : ", flag);
        return flag.id === ship.flag;
      });
      const associatedVesselType = vesselTypes.find(
        (vessel) => vessel.id === ship.ship_type
      );
      // console.log("", associatedCompany);
      const shipIns = {
        id: ship.id,
        name: ship.ship_name,
        typeId: ship.ship_type || "N/A",
        type: associatedVesselType?.name || "N/A",
        companyID: ship.company || "N/A",
        associatedWithCompany: associatedCompany?.company_name || "N/A",
        shipCrew: ship.crew || [],
        jobOrdersCount: ship.jobs_order_count || 0,
        jobOrders: ship.job_orders,
        crewCount: Array.isArray(ship.crew) ? ship.crew.length : 0,
        imoNumber: ship.imo_number || "N/A",
        status: ship.status || "N/A",
        flagId: ship.flag || "N/A",
        flag: ship.flag_name || associatedFlags?.name || "N/A",
        grossTonnage: ship.gross_tonnage || 0,
        deadweight: ship.deadweight || 0,
        engineType: ship.engine_type || "N/A",
        enginePower: ship.engine_power_kw || 0,
        yearBuilt: ship.year_built || "N/A",
        officialNo: ship.official_no || "N/A",
        avatar: ASSETS.LOGO,
        _original: ship,
      };
      return shipIns;
    });
  }, [backendCompanies, backendShips, flags, vesselTypes]);

  // ============================================
  // COMPANY CRUD HANDLERS
  // ============================================
  const handleViewCompany = useCallback(
    (row) => {
      // Find full company object
      const company = backendCompanies.find((c) => c.id === row.id);
      if (company) {
        setViewingCompany(company);
        setShowCompanyViewModal(true);
      } else {
        notify.error("Company data not found");
      }
    },
    [backendCompanies, notify]
  );

  const handleEditCompany = useCallback(
    (row) => {
      if (!canEdit) {
        notify.error("You do not have permission to edit companies");
        return;
      }
      const company = backendCompanies.find((c) => c.id === row.id);
      // console.log("the editing company is : ", company);
      if (company) {
        setSelectedCompany(company);
        setShowCompanyModal(true);
      }
    },
    [backendCompanies, canEdit, notify]
  );

  const handleDeleteCompany = useCallback(
    (id) => {
      if (!canDelete) {
        notify.error("You do not have permission to delete companies");
        return;
      }
      setItemToDelete(id);
      setDeleteType("company");
      setShowDeleteConfirm(true);
    },
    [canDelete, notify]
  );

  const handleAddCompany = useCallback(() => {
    if (!canCreate) {
      notify.error("You do not have permission to add companies");
      return;
    }
    setSelectedCompany(null);
    setShowCompanyModal(true);
  }, [canCreate, notify]);

  const handleSaveCompany = async (companyData) => {
    if (selectedCompany) {
      const result = await updateCompany(selectedCompany.id, companyData);
      if (result.success) {
        setShowCompanyModal(false);
        await loadCompanyStats();
      }
    } else {
      const result = await createCompany(companyData);
      if (result.success) {
        setShowCompanyModal(false);
        await loadCompanyStats();
      }
    }
  };

  // ✅ NEW: Download individual company
  const handleDownloadCompany = useCallback(
    (row) => {
      try {
        const companyDetails = {
          Name: row.name,
          Type: row.type,
          Email: row.email,
          "Open Positions": row.openPositions,
          Status: row.status,
        };

        const blob = new Blob([JSON.stringify(companyDetails, null, 2)], {
          type: "application/json",
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `Company_${row.name.replace(/\s+/g, "_")}.json`;
        a.click();
        URL.revokeObjectURL(url);

        notify.success("Company details downloaded!");
      } catch (error) {
        notify.error("Failed to download");
        console.error(error);
      }
    },
    [notify]
  );

  // ============================================
  // SHIP CRUD HANDLERS
  // ============================================
  const handleViewShip = useCallback(
    (row) => {
      const ship = backendShips.find((s) => s.id === row.id);
      if (ship) {
        // Augment ship with resolved names if needed, though ShipViewModal handles ids somewhat
        // But the row object has resolved names. Let's merge or use row._original + resolved props.
        // Actually row._original is what we want mostly, but row has resolved company name etc.
        // Let's pass the row which contains _original + derived fields, or just find from backend.
        // The ViewModal expects raw fields mostly but display components handle it. 
        // Let's pass the backend object but maybe augment it with display names from row if needed.
        // Actually ShipViewModal handles `associatedWithCompany` prop or `company_name`.
        // Let's pass the backend ship object mixed with row for display names.
        const displayShip = {
          ...ship,
          associatedWithCompany: row.associatedWithCompany,
          flagName: row.flag,
          typeName: row.type
        };
        setViewingShip(displayShip);
        setShowShipViewModal(true);
      } else {
        notify.error("Ship data not found");
      }
    },
    [backendShips, notify]
  );

  const handleEditShip = useCallback(
    (row) => {
      if (!canEdit) {
        notify.error("You do not have permission to edit ships");
        return;
      }
      const ship = backendShips.find((s) => s.id === row.id);
      if (ship) {
        setSelectedShip(ship);
        setShowShipModal(true);
      }
    },
    [backendShips, canEdit, notify]
  );

  const handleDeleteShip = useCallback(
    (id) => {
      if (!canDelete) {
        notify.error("You do not have permission to delete ships");
        return;
      }
      setItemToDelete(id);
      setDeleteType("ship");
      setShowDeleteConfirm(true);
    },
    [canDelete, notify]
  );

  const handleAddShip = useCallback(() => {
    if (!canCreate) {
      notify.error("You do not have permission to add ships");
      return;
    }
    setSelectedShip(null);
    setShowShipModal(true);
  }, [canCreate, notify]);

  const handleSaveShip = async (shipData) => {
    // Separate crew data from technical data
    const { crew: newCrewIds = [], ...techData } = shipData;

    // Get current IDs if editing
    const oldCrewIds = selectedShip?.crew ?
      selectedShip.crew.map(u => typeof u === 'object' ? u.id : u) :
      [];

    let shipId = selectedShip?.id;
    let result;

    // 1. Update/Create ship record (technical details)
    if (selectedShip) {
      result = await updateShip(selectedShip.id, techData);
    } else {
      result = await createShip(techData);
      if (result.success) shipId = result.data.id;
    }

    // 2. If technical save successful, handle crew assignments manually (one by one as per BE requirements)
    if (result.success) {
      // IDs to add: in new list but not in old
      const usersToAdd = newCrewIds.filter(id => !oldCrewIds.includes(id));
      // IDs to remove: in old list but not in new
      const usersToRemove = oldCrewIds.filter(id => !newCrewIds.includes(id));

      // Process assignments sequentially
      // Note: we use for...of for sequential execution to avoid hammering or race conditions
      for (const userId of usersToAdd) {
        await assignUser(shipId, userId);
      }

      // Process removals sequentially
      for (const userId of usersToRemove) {
        await unassignUser(shipId, userId);
      }

      setShowShipModal(false);

      // Refresh ships list to show updated counts/data
      fetchShips({ page: shipPagination.currentPage || 1 });
    }
  };

  // ============================================
  // JOB ORDER CRUD HANDLERS
  // ============================================
  const handleAddJobOrder = useCallback(() => {
    if (!canCreate) {
      notify.error("You do not have permission to create job orders");
      return;
    }
    setSelectedJobOrder(null);
    setShowJobOrderModal(true);
  }, [canCreate, notify]);

  const handleEditJobOrder = useCallback(
    (row) => {
      if (!canEdit) {
        notify.error("You do not have permission to edit job orders");
        return;
      }
      const jo = backendJobOrders.find((j) => j.id === row.id);
      if (jo) {
        setSelectedJobOrder(jo);
        setShowJobOrderModal(true);
      }
    },
    [backendJobOrders, canEdit, notify]
  );

  const handleDeleteJobOrder = useCallback(
    (id) => {
      if (!canDelete) {
        notify.error("You do not have permission to delete job orders");
        return;
      }
      setItemToDelete(id);
      setDeleteType("job_order");
      setShowDeleteConfirm(true);
    },
    [canDelete, notify]
  );

  const handleSaveJobOrder = async (data) => {
    if (selectedJobOrder) {
      const result = await updateJobOrder(selectedJobOrder.id, data);
      if (result.success) setShowJobOrderModal(false);
    } else {
      const result = await createJobOrder(data);
      if (result.success) setShowJobOrderModal(false);
    }
  };

  const handleApplyJobOrderFilters = useCallback(() => {
    setActiveJobOrderFilters(jobOrderFilters);
    setShowJobOrderFilterModal(false);
    fetchJobOrders({ ...jobOrderFilters, page: 1 });
  }, [jobOrderFilters, fetchJobOrders]);

  const handleResetJobOrderFilters = useCallback(() => {
    const empty = {
      company: "",
      ship: "",
      status: "",
      reference_number: "",
      request_date_from: "",
      request_date_to: ""
    };
    setJobOrderFilters(empty);
    setActiveJobOrderFilters(empty);
    setShowJobOrderFilterModal(false);
    fetchJobOrders({ page: 1 });
  }, [fetchJobOrders]);

  const handleJobOrderPageChange = useCallback(
    (newPage) => {
      fetchJobOrders({ ...activeJobOrderFilters, page: newPage });
    },
    [fetchJobOrders, activeJobOrderFilters]
  );

  // ============================================
  // RANK CRUD HANDLERS
  // ============================================
  const handleAddRank = useCallback(() => {
    if (!canCreate) {
      notify.error("You do not have permission to create ranks");
      return;
    }
    setSelectedRank(null);
    setShowRankModal(true);
  }, [canCreate, notify]);

  const handleEditRank = useCallback(
    (row) => {
      if (!canEdit) {
        notify.error("You do not have permission to edit ranks");
        return;
      }
      setSelectedRank(row);
      setShowRankModal(true);
    },
    [canEdit, notify]
  );

  const handleDeleteRank = useCallback(
    (id) => {
      if (!canDelete) {
        notify.error("You do not have permission to delete ranks");
        return;
      }
      setItemToDelete(id);
      setDeleteType("rank");
      setShowDeleteConfirm(true);
    },
    [canDelete, notify]
  );

  const handleConfirmDelete = useCallback(async () => {
    if (!itemToDelete || !deleteType) return;

    let result;
    switch (deleteType) {
      case "company":
        result = await deleteCompany(itemToDelete);
        if (result.success) await loadCompanyStats();
        break;
      case "ship":
        result = await deleteShip(itemToDelete);
        break;
      case "job_order":
        result = await deleteJobOrder(itemToDelete);
        break;
      case "rank":
        result = await deleteRank(itemToDelete);
        break;
      default:
        break;
    }

    if (result && result.success) {
      setShowDeleteConfirm(false);
      setItemToDelete(null);
      setDeleteType(null);
    }
  }, [itemToDelete, deleteType, deleteCompany, deleteShip, deleteJobOrder, deleteRank, loadCompanyStats]);

  const handleSaveRank = async (rankData) => {
    if (selectedRank) {
      const result = await updateRank(selectedRank.id, rankData);
      if (result.success) setShowRankModal(false);
    } else {
      const result = await createRank(rankData);
      if (result.success) setShowRankModal(false);
    }
  };

  // ============================================
  // CREW MANAGEMENT HANDLER
  // ============================================
  const handleManageCrew = useCallback((shipRow) => {
    setTargetShipForCrew(shipRow);
    setShowCrewModal(true);
  }, []);

  const handleManageJobOrders = useCallback((companyRow) => {
    setTargetCompanyForJobOrder(companyRow);
    setShowJobOrderModal(true);
  }, []);

  // ✅ NEW: Download individual ship
  const handleDownloadShip = useCallback(
    (row) => {
      try {
        const shipDetails = {
          Name: row.name,
          "IMO Number": row.imoNumber,
          Flag: row.flag,
          Type: row.type,
          Company: row.company,
          Status: row.status,
        };

        const blob = new Blob([JSON.stringify(shipDetails, null, 2)], {
          type: "application/json",
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `Ship_${row.name.replace(/\s+/g, "_")}.json`;
        a.click();
        URL.revokeObjectURL(url);

        notify.success("Ship details downloaded!");
      } catch (error) {
        notify.error("Failed to download");
        console.error(error);
      }
    },
    [notify]
  );

  // ✅ Backend Filter Handlers for Companies
  const handleApplyCompanyFilters = useCallback(() => {
    setActiveCompanyFilters(companyFilters);
    setShowCompanyFilterModal(false);
    fetchCompanies({ ...companyFilters, page: 1 });
  }, [companyFilters, fetchCompanies]);

  const handleResetCompanyFilters = useCallback(() => {
    const emptyFilters = { name: "", status: "", company_type: "" };
    setCompanyFilters(emptyFilters);
    setActiveCompanyFilters(emptyFilters);
    setShowCompanyFilterModal(false);
    fetchCompanies({ page: 1 });
  }, [fetchCompanies]);

  // ✅ Backend Filter Handlers for Ships
  const handleApplyShipFilters = useCallback(() => {
    setActiveShipFilters(shipFilters);
    setShowShipFilterModal(false);
    fetchShips({ ...shipFilters, page: 1 });
  }, [shipFilters, fetchShips]);

  const handleResetShipFilters = useCallback(() => {
    const emptyFilters = {
      name: "",
      imo_number: "",
      company: "",
      status: "",
      vessel_type: "",
    };
    setShipFilters(emptyFilters);
    setActiveShipFilters(emptyFilters);
    setShowShipFilterModal(false);
    fetchShips({ page: 1 });
  }, [fetchShips]);

  // Handle page changes
  const handleCompanyPageChange = useCallback((newPage) => {
    fetchCompanies({ ...activeCompanyFilters, page: newPage });
  }, [fetchCompanies, activeCompanyFilters]);

  // Handle ship page changes
  const handleShipPageChange = useCallback(
    (newPage) => {
      fetchShips({ ...activeShipFilters, page: newPage });
    },
    [fetchShips, activeShipFilters]
  );

  // ✅ NEW: Export handlers - UPDATED to use backend data
  const handleExportCompaniesExcel = useCallback(() => {
    try {
      const dataToExport = companyData.map(
        ({ id, avatar, _original, ...rest }) => rest
      );
      exportToExcel(
        dataToExport,
        `Companies_Export_${new Date().toISOString().split("T")[0]}.xlsx`,
        "Companies"
      );
      notify.success("Companies exported to Excel!");
    } catch (error) {
      notify.error("Failed to export");
    }
  }, [companyData, notify]);


  const handleExportShipsExcel = useCallback(() => {
    try {
      const dataToExport = shipData.map(
        ({ id, avatar, _original, ...rest }) => rest
      );
      exportToExcel(
        dataToExport,
        `Ships_Export_${new Date().toISOString().split("T")[0]}.xlsx`,
        "Ships"
      );
      notify.success("Ships exported to Excel!");
    } catch (error) {
      notify.error("Failed to export");
    }
  }, [shipData, notify]);

  const handleRefreshCompanies = useCallback(() => {
    fetchCompanies({ ...activeCompanyFilters, page: 1 });
  }, [fetchCompanies, activeCompanyFilters]);

  const handleRefreshShips = useCallback(() => {
    fetchShips({ ...activeShipFilters, page: 1 });
  }, [fetchShips, activeShipFilters]);

  // ✅ NEW: Saved filters handlers
  const handleApplyCompanyPreset = useCallback(
    (preset) => {
      setCompanyFilters(preset);
      setActiveCompanyFilters(preset);
      fetchCompanies({ ...preset, page: 1 });
    },
    [fetchCompanies]
  );

  const handleSaveCompanyPreset = useCallback((name, filterValues) => {
    setSavedCompanyPresets((prev) => [
      ...prev,
      { name, filters: filterValues },
    ]);
  }, []);

  const handleDeleteCompanyPreset = useCallback((name) => {
    setSavedCompanyPresets((prev) => prev.filter((p) => p.name !== name));
  }, []);

  const handleApplyShipPreset = useCallback(
    (preset) => {
      setShipFilters(preset);
      setActiveShipFilters(preset);
    },
    [setShipFilters, setActiveShipFilters]
  );

  const handleSaveShipPreset = useCallback((name, filterValues) => {
    setSavedShipPresets((prev) => [...prev, { name, filters: filterValues }]);
  }, []);

  const handleDeleteShipPreset = useCallback((name) => {
    setSavedShipPresets((prev) => prev.filter((p) => p.name !== name));
  }, []);

  // Table columns
  const companyColumns = useMemo(
    () => [
      {
        key: "name",
        title: "Company Name",
        width: 360,
        showAvatar: true,
        sortable: true,
        render: (value, row) => row.name,
      },
      {
        key: "companyFlag",
        title: "Country",
        width: 100,
        sortable: true,
        render: (value) => value || "—",
      },
      {
        key: "type",
        title: "Type",
        width: 350,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "openPositions",
        title: "Jobs",
        width: 80,
        sortable: true,
        render: (value) => value,
      },
      // {
      //   key: "hourRate",
      //   title: "Rate/Hr",
      //   width: 100,
      //   sortable: true,
      //   render: (value) => `$${value}`,
      // },
      {
        key: "website",
        title: "Website",
        width: 300,
        sortable: true,
        render: (value, row) => {
          if (!row.website) return "—";
          return (
            <a
              href={row.website}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              style={{
                color: "#3B82F6",
                textDecoration: "underline",
                cursor: "pointer",
                fontSize: "inherit",
              }}
            >
              {value}
            </a>
          );
        },
      },
      {
        key: "email",
        title: "Email",
        width: 250,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "status",
        title: "Status",
        width: 120,
        sortable: true,
        isStatus: true,
        headerAlign: "center",
        headerTextAlign: "center",
        render: (value) => value,
      },
      {
        key: "actions",
        title: "Actions",
        width: 100,
        isActions: true,
        onUser: handleViewCompany, // Maps to "View Profile"
        onEdit: canEdit ? handleEditCompany : undefined,
        onDelete: canDelete ? handleDeleteCompany : undefined,
        onDownload: handleDownloadCompany,
        onVacancy: canEdit ? (row) => handleManageJobOrders(row) : undefined,
      },
    ],
    [
      canEdit,
      canDelete,
      handleDeleteCompany,
      handleEditCompany,
      handleViewCompany,
      handleDownloadCompany,
      handleManageJobOrders,
    ]
  );

  const shipColumns = useMemo(
    () => [
      {
        key: "name",
        title: "Ship Name",
        width: 400,
        showAvatar: true,
        sortable: true,
        render: (value, row) => row.name,
      },
      {
        key: "imoNumber",
        title: "IMO Number",
        width: 120,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "flag",
        title: "Flag",
        width: 120,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "type",
        title: "Type",
        width: 200,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "associatedWithCompany",
        title: "Company",
        width: 300,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "jobOrdersCount",
        title: "Jobs",
        width: 80,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "crewCount",
        title: "Crew",
        width: 80,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "grossTonnage",
        title: "GT",
        width: 80,
        sortable: true,
        render: (v) => v,
      },
      {
        key: "deadweight",
        title: "DWT",
        width: 80,
        sortable: true,
        render: (v) => v,
      },
      {
        key: "engineType",
        title: "Engine",
        width: 120,
        sortable: true,
        render: (v) => v,
      },
      {
        key: "yearBuilt",
        title: "Year",
        width: 80,
        sortable: true,
        render: (v) => v,
      },
      {
        key: "enginePower",
        title: "Power",
        width: 100,
        sortable: true,
        render: (v) => `${v} kW`,
      },
      {
        key: "officialNo",
        title: "Official No",
        width: 120,
        sortable: true,
        render: (v) => v,
      },
      {
        key: "status",
        title: "Status",
        width: 120,
        sortable: true,
        isStatus: true,
        headerAlign: "center",
        headerTextAlign: "center",
        render: (value) => value,
      },
      {
        key: "actions",
        title: "Actions",
        width: 140, // Increased for crew action
        isActions: true,
        onUser: handleViewShip,
        onEdit: canEdit ? handleEditShip : undefined,
        onDelete: canDelete ? handleDeleteShip : undefined,
        onDownload: handleDownloadShip,
        onCrew: handleManageCrew, // Custom action for crew management
      },
    ],
    [canEdit, canDelete, handleDeleteShip, handleEditShip, handleDownloadShip, handleViewShip, handleManageCrew]
  );

  // Ranks table columns
  const rankColumns = useMemo(
    () => [
      {
        key: "rank_name",
        title: "Rank Name",
        width: 250,
        sortable: true,
        render: (v) => v,
      },
      {
        key: "rank_code",
        title: "Code",
        width: 150,
        sortable: true,
        render: (v) => v,
      },
      {
        key: "actions",
        title: "Actions",
        width: 100,
        isActions: true,
        onEdit: canEdit ? handleEditRank : undefined,
        onDelete: canDelete ? handleDeleteRank : undefined,
      },
    ],
    [canEdit, canDelete, handleEditRank, handleDeleteRank]
  );

  // ✅ NEW: Enhanced filter fields aligned with BE documentation
  const companyFilterFields = [
    {
      key: "name",
      label: "Company Name",
      type: "text",
      placeholder: "Search by name...",
    },
    {
      key: "status",
      label: "Status",
      type: "select",
      placeholder: "All Statuses",
      options: [
        { value: "Active", label: "Active" },
        { value: "Inactive", label: "Inactive" },
        { value: "Prospect", label: "Prospect" },
      ],
    },
    {
      key: "company_type",
      label: "Company Type",
      type: "select",
      placeholder: "All Types",
      options: [
        { value: "Shipping Manning Companies", label: "Shipping Manning Companies" },
        { value: "Cargo Manning Companies", label: "Cargo Manning Companies" },
        { value: "Cruise & Hospitality Manning Companies", label: "Cruise & Hospitality Manning Companies" },
        { value: "Offshore & Oil/Gas Manning Companies", label: "Offshore & Oil/Gas Manning Companies" },
        { value: "Fishing Fleet Manning Companies", label: "Fishing Fleet Manning Companies" },
        { value: "General Crew Manning Companies", label: "General Crew Manning Companies" },
        { value: "Specialized Marine Manning Companies", label: "Specialized Marine Manning Companies" },
        { value: "Temporary / Contract Manning Agencies", label: "Temporary / Contract Manning Agencies" },
        { value: "Full Crew Management Companies", label: "Full Crew Management Companies" },
      ],
    },
  ];

  const shipFilterFields = [
    {
      key: "name",
      label: "Ship Name",
      type: "text",
      placeholder: "Search by ship name...",
    },
    {
      key: "imo_number",
      label: "IMO Number",
      type: "text",
      placeholder: "Search by IMO number...",
    },
    {
      key: "company",
      label: "Company",
      type: "select",
      placeholder: "All Companies",
      options: referenceOptions.companies,
    },
    {
      key: "status",
      label: "Status",
      type: "select",
      placeholder: "All Statuses",
      options: [
        { value: "Active", label: "Active" },
        { value: "Under Maintenance", label: "Under Maintenance" },
        { value: "Inactive", label: "Inactive" },
      ],
    },
    {
      key: "vessel_type",
      label: "Ship Type",
      type: "select",
      placeholder: "All Types",
      options: [
        { value: "Container Ships", label: "Container Ships" },
        { value: "Bulk Carriers", label: "Bulk Carriers" },
        { value: "Tankers", label: "Tankers" },
        { value: "Ro-Ro Ships", label: "Ro-Ro Ships" },
        { value: "Passenger Ships", label: "Passenger Ships" },
        { value: "Fishing Vessels", label: "Fishing Vessels" },
        { value: "Recreational", label: "Recreational" },
        { value: "Offshore Support Vessels", label: "Offshore Support Vessels" },
        { value: "Icebreakers", label: "Icebreakers" },
        { value: "Tugboats", label: "Tugboats" },
      ],
    },
  ];

  // Job Orders data transform
  const jobOrderData = useMemo(() => {
    return backendJobOrders.map((jo) => {
      const company = backendCompanies.find((c) => c.id === jo.company);
      const ship = backendShips.find((s) => s.id === jo.ship);
      return {
        id: jo.id,
        referenceNumber: jo.reference_number || "N/A",
        companyName: jo.company_name || company?.company_name || "N/A",
        shipName: jo.ship_name || ship?.ship_name || "N/A",
        requestDate: jo.request_date || "",
        targetJoiningDate: jo.target_joining_date || "",
        tradingArea: jo.trading_area || "N/A",
        status: jo.status || "Open",
        _original: jo,
      };
    });
  }, [backendJobOrders, backendCompanies, backendShips]);

  // Job Orders table columns
  // const jobOrderColumns = useMemo(
  //   () => [
  //     {
  //       key: "referenceNumber",
  //       title: "Reference",
  //       width: 140,
  //       sortable: true,
  //       render: (v) => v,
  //     },
  //     {
  //       key: "companyName",
  //       title: "Company",
  //       width: 180,
  //       sortable: true,
  //       render: (v) => v,
  //     },
  //     {
  //       key: "shipName",
  //       title: "Ship",
  //       width: 150,
  //       sortable: true,
  //       render: (v) => v,
  //     },
  //     {
  //       key: "requestDate",
  //       title: "Request Date",
  //       width: 110,
  //       sortable: true,
  //       render: (v) => v,
  //     },
  //     {
  //       key: "tradingArea",
  //       title: "Trading Area",
  //       width: 140,
  //       sortable: true,
  //       render: (v) => v,
  //     },
  //     {
  //       key: "status",
  //       title: "Status",
  //       width: 100,
  //       sortable: true,
  //       isStatus: true,
  //       headerAlign: "center",
  //       headerTextAlign: "center",
  //       render: (v) => v,
  //     },
  //     {
  //       key: "actions",
  //       title: "Actions",
  //       width: 100,
  //       isActions: true,
  //       onEdit: canEdit ? handleEditJobOrder : undefined,
  //       onDelete: canDelete ? handleDeleteJobOrder : undefined,
  //     },
  //   ],
  //   [canEdit, canDelete, handleEditJobOrder, handleDeleteJobOrder]
  // );

  const headerHeight = Math.round(101 * scale);

  return (
    <main style={getMainContainerStyles(scale, headerHeight)}>
      <style>{generateAllPageStyles(scale)}</style>

      {/* Companies Section */}
      <section style={{ marginBottom: `${Math.round(13 * scale)}px` }}>
        <div style={getRowBetweenStyles(scale)}>
          <h2
            style={{
              ...getPageTitleStyles(scale),
              marginBottom: `${Math.round(8 * scale)}px`,
            }}
          >
            Manage Companies positions
          </h2>

          {/* ✅ NEW: Saved Filters */}
          <SavedFilters
            scale={scale}
            savedPresets={savedCompanyPresets}
            currentFilters={activeCompanyFilters}
            onApplyPreset={handleApplyCompanyPreset}
            onSavePreset={handleSaveCompanyPreset}
            onDeletePreset={handleDeleteCompanyPreset}
          />

          <div
            style={{
              display: "flex",
              marginTop: `${Math.round(20 * scale)}px`,
              gap: `${Math.round(8 * scale)}px`,
              alignItems: "center"
            }}
          >
            <Button
              variant="icon"
              onClick={() => setShowCompanyFilterModal(true)}
              ariaLabel="Filter companies"
              title="Filter companies"
              scale={scale}
              style={{ width: 30, height: 30, borderRadius: 8, minHeight: 30 }}
            >
              <svg
                width={16}
                height={16}
                viewBox="0 0 24 24"
                fill="none"
              >
                <path
                  d="M3 6h18M6 12h12M9 18h6"
                  stroke="#1E1E1E"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
              </svg>
            </Button>
            <Button
              variant="icon"
              onClick={handleRefreshCompanies}
              ariaLabel="Press to refresh the table"
              title="Press to refresh the table"
              scale={scale}
              style={{ width: 30, height: 30, borderRadius: 8, minHeight: 30 }}
            >
              <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
                <path d="M21 3v5h-5" />
                <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
                <path d="M8 16H3v5" />
              </svg>
            </Button>
            {canCreate && (
              <Button
                variant="primary"
                onClick={handleAddCompany}
                scale={scale}
                style={{ minHeight: 30, height: 30, padding: "0 14px", fontSize: 13, borderRadius: 8, fontWeight: 500, lineHeight: "30px" }}
              >
                Add Company
              </Button>
            )}
            {companyData.length > 0 && (
              <>
                <Button
                  variant="outline"
                  onClick={handleExportCompaniesExcel}
                  scale={scale}
                  style={{ minHeight: 30, height: 30, padding: "0 14px", fontSize: 13, borderRadius: 8, fontWeight: 500, lineHeight: "30px" }}
                >
                  Export Excel
                </Button>
              </>
            )}
          </div>
        </div>

        <RefinedDataTable
          data={companyData}
          columns={companyColumns}
          rowKey="id"
          scale={scale}
          pageSize={25}
          initialPage={1}
          hidePagination={true} // Hide internal pagination, use backend pagination below
          actions={
            canEdit && canDelete
              ? ["Edit", "Download", "Delete"]
              : canEdit
                ? ["Edit", "Download"]
                : canDelete
                  ? ["Download", "Delete"]
                  : ["Download"]
          }
          onRowClick={handleViewCompany}
          styleOverrides={{ columnGap: 9 }}
          loading={companiesLoading}
        />

        {/* Company Pagination */}
        {/* <Pagination
          page={companyPagination.currentPage}
          pageSize={25} // Default page size
          total={companyPagination.count}
          onChange={handleCompanyPageChange}
          scale={scale}
          showInfo={true}
        /> */}
      </section>

      {/* Ships Section */}
      <section>
        <div style={getRowBetweenStyles(scale)}>
          <h2
            style={{
              ...getPageTitleStyles(scale),
              marginBottom: `${Math.round(8 * scale)}px`,
            }}
          >
            Manage Ship Management
          </h2>

          {/* ✅ NEW: Saved Filters */}
          <SavedFilters
            scale={scale}
            savedPresets={savedShipPresets}
            currentFilters={activeShipFilters}
            onApplyPreset={handleApplyShipPreset}
            onSavePreset={handleSaveShipPreset}
            onDeletePreset={handleDeleteShipPreset}
          />

          <div
            style={{
              display: "flex",
              justifyContent: "flex-end",
              marginTop: `${Math.round(20 * scale)}px`,
              gap: `${Math.round(8 * scale)}px`,
              alignItems: "center"
            }}
          >
            <Button
              variant="icon"
              onClick={() => setShowShipFilterModal(true)}
              ariaLabel="Filter ships"
              title="Filter ships"
              scale={scale}
              style={{ width: 30, height: 30, borderRadius: 8, minHeight: 30 }}
            >
              <svg
                width={16}
                height={16}
                viewBox="0 0 24 24"
                fill="none"
              >
                <path
                  d="M3 6h18M6 12h12M9 18h6"
                  stroke="#1E1E1E"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
              </svg>
            </Button>
            <Button
              variant="icon"
              onClick={handleRefreshShips}
              ariaLabel="Press to refresh the table"
              title="Press to refresh the table"
              scale={scale}
              style={{ width: 30, height: 30, borderRadius: 8, minHeight: 30 }}
            >
              <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
                <path d="M21 3v5h-5" />
                <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
                <path d="M8 16H3v5" />
              </svg>
            </Button>
            {canCreate && (
              <Button variant="primary" onClick={handleAddShip} scale={scale} style={{ minHeight: 30, height: 30, padding: "0 14px", fontSize: 13, borderRadius: 8, fontWeight: 500, lineHeight: "30px" }}>
                Add Ship
              </Button>
            )}
            {shipData.length > 0 && (
              <>
                <Button
                  variant="outline"
                  onClick={handleExportShipsExcel}
                  scale={scale}
                  style={{ minHeight: 30, height: 30, padding: "0 14px", fontSize: 13, borderRadius: 8, fontWeight: 500, lineHeight: "30px" }}
                >
                  Export Excel
                </Button>
              </>
            )}
          </div>
        </div>

        <ExpandableDataTable
          data={shipData}
          columns={shipColumns}
          rowKey="id"
          scale={scale}
          pageSize={25}
          hidePagination={true}
          initialPage={1}
          expandable={true}
          renderExpandedRow={(row) => {
            const shipJobOrders = backendJobOrders.filter(jo => jo.ship === row.id);
            if (!shipJobOrders || shipJobOrders.length === 0) {
              return (
                <div style={{ color: COLORS.lightText, fontSize: Math.round(14 * scale), fontStyle: "italic", padding: "12px 0" }}>
                  No job orders assigned to this ship.
                </div>
              );
            }
            return (
              <div style={{ padding: `${Math.round(8 * scale)}px 0` }}>
                <h4 style={{ margin: 0, marginBottom: Math.round(12 * scale), color: COLORS.primary, fontSize: Math.round(14 * scale), fontWeight: 600 }}>Associated Job Orders</h4>
                <div style={{ display: "flex", flexDirection: "column", gap: Math.round(8 * scale) }}>
                  {shipJobOrders.map(jo => (
                    <div key={jo.id} style={{
                      border: `1px solid ${COLORS.borderColor}`,
                      borderRadius: Math.round(6 * scale),
                      padding: Math.round(12 * scale),
                      background: COLORS.white
                    }}>
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: Math.round(8 * scale) }}>
                        <div style={{ fontWeight: 500, color: COLORS.darkText, fontSize: Math.round(13 * scale) }}>Reference: {jo.reference_number || 'N/A'}</div>
                        <div style={{ fontSize: Math.round(12 * scale), color: COLORS.lightText }}>Status: {jo.status || 'Active'}</div>
                      </div>
                      {jo.positions && jo.positions.length > 0 ? (
                        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: Math.round(8 * scale) }}>
                          {jo.positions.map(pos => (
                            <div key={pos.id} style={{ background: COLORS.cardBg, padding: Math.round(8 * scale), borderRadius: Math.round(4 * scale), fontSize: Math.round(12 * scale), display: "flex", justifyContent: "space-between" }}>
                              <span style={{ color: COLORS.darkText }}>{pos.rank_name || pos.rank || 'N/A'}</span>
                              <span style={{ color: COLORS.primary, fontWeight: 500 }}>{pos.quantity || 1} needed</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div style={{ fontSize: Math.round(12 * scale), color: COLORS.lightText }}>No positions defined for this order.</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            );
          }}
          actions={
            canEdit && canDelete
              ? ["Edit", "Download", "Delete"]
              : canEdit
                ? ["Edit", "Download"]
                : canDelete
                  ? ["Download", "Delete"]
                  : ["Download"]
          }
          onRowClick={handleViewShip}
          styleOverrides={{ columnGap: 9 }}
          loading={shipsLoading}
        />
        {/* Ship Pagination */}
        {/* <Pagination
          page={shipPagination.currentPage || 1}
          pageSize={25}
          total={shipPagination.count || 0}
          onChange={handleShipPageChange}
          scale={scale}
          showInfo={true}
        /> */}
      </section>

      {/* ── Job Orders Section ─────────────────────────────────────────── */}
      {/* <section style={{ marginBottom: `${Math.round(13 * scale)}px` }}>
        <div style={getRowBetweenStyles(scale)}>
          <h2
            style={{
              ...getPageTitleStyles(scale),
              marginBottom: `${Math.round(8 * scale)}px`,
            }}
          >
            Job Orders
          </h2>

          <div
            style={{
              display: "flex",
              justifyContent: "flex-end",
              marginTop: `${Math.round(20 * scale)}px`,
              gap: `${Math.round(12 * scale)}px`,
            }}
          >
            <Button
              variant="icon"
              onClick={() => setShowJobOrderFilterModal(true)}
              ariaLabel="Filter job orders"
              title="Filter job orders"
              scale={scale}
            >
              <svg width={Math.round(21 * scale)} height={Math.round(21 * scale)} viewBox="0 0 24 24" fill="none">
                <path d="M3 6h18M6 12h12M9 18h6" stroke="#1E1E1E" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </Button>
            {canCreate && (
              <Button variant="primary" onClick={handleAddJobOrder} scale={scale}>
                Add Job Order
              </Button>
            )}
          </div>
        </div>

        {/* <RefinedDataTable
          data={jobOrderData}
          columns={jobOrderColumns}
          rowKey="id"
          scale={scale}
          pageSize={25}
          hidePagination={true}
          initialPage={1}
          actions={
            canEdit && canDelete
              ? ["Edit", "Delete"]
              : canEdit
                ? ["Edit"]
                : canDelete
                  ? ["Delete"]
                  : []
          }
          styleOverrides={{ columnGap: 9 }}
          loading={jobOrdersLoading}
        /> */}
      {/* <Pagination
          page={jobOrderPagination.currentPage || 1}
          pageSize={25}
          total={jobOrderPagination.count || 0}
          onChange={handleJobOrderPageChange}
          scale={scale}
          showInfo={true}
        /> */}
      {/* </section> */}
      {/* */}

      {/* ── Ranks Section ─────────────────────────────────────────────── */}
      {/* <section>
        <div style={getRowBetweenStyles(scale)}>
          <h2
            style={{
              ...getPageTitleStyles(scale),
              marginBottom: `${Math.round(8 * scale)}px`,
            }}
          >
            Rank Codes (Core)
          </h2>

          <div
            style={{
              display: "flex",
              justifyContent: "flex-end",
              marginTop: `${Math.round(20 * scale)}px`,
              gap: `${Math.round(12 * scale)}px`,
            }}
          >
            {canCreate && (
              <Button variant="primary" onClick={handleAddRank} scale={scale}>
                Add Rank
              </Button>
            )}
          </div>
        </div>

        <RefinedDataTable
          data={backendRanks}
          columns={rankColumns}
          rowKey="id"
          scale={scale}
          pageSize={25}
          hidePagination={true}
          initialPage={1}
          actions={
            canEdit && canDelete
              ? ["Edit", "Delete"]
              : canEdit
                ? ["Edit"]
                : canDelete
                  ? ["Delete"]
                  : []
          }
          styleOverrides={{ columnGap: 9 }}
          loading={ranksLoading}
        />
      </section> */}

      {/* ✅ MODALS - Companies */}
      <EnhancedFilterModel
        isOpen={showCompanyFilterModal}
        onClose={() => setShowCompanyFilterModal(false)}
        title="Filter Companies"
        fields={companyFilterFields}
        values={companyFilters}
        onValuesChange={setCompanyFilters}
        onApply={handleApplyCompanyFilters}
        onReset={handleResetCompanyFilters}
        scale={scale}
      />

      {showCompanyModal && (
        <CompanyFormModal
          company={selectedCompany}
          onClose={() => setShowCompanyModal(false)}
          onSave={handleSaveCompany}
          scale={scale}
        />
      )}

      {/* ✅ MODALS - Ships */}
      <EnhancedFilterModel
        isOpen={showShipFilterModal}
        onClose={() => setShowShipFilterModal(false)}
        title="Filter Ships"
        fields={shipFilterFields}
        values={shipFilters}
        onValuesChange={setShipFilters}
        onApply={handleApplyShipFilters}
        onReset={handleResetShipFilters}
        scale={scale}
      />

      {showShipModal && (
        <ShipFormModal
          ship={selectedShip}
          companies={backendCompanies}
          onClose={() => setShowShipModal(false)}
          onSave={handleSaveShip}
          scale={scale}
        />
      )}

      {/* ── MODALS — Job Orders ──────────────────────────────────────── */}
      {/* <EnhancedFilterModel
        isOpen={showJobOrderFilterModal}
        onClose={() => setShowJobOrderFilterModal(false)}
        title="Filter Job Orders"
        fields={[
          {
            key: "reference_number",
            label: "Reference Number",
            type: "text",
            placeholder: "Search by reference...",
          },
          {
            key: "company",
            label: "Company",
            type: "select",
            placeholder: "All Companies",
            options: backendCompanies.map(c => ({ value: c.id, label: c.company_name })),
          },
          {
            key: "ship",
            label: "Ship",
            type: "select",
            placeholder: "All Ships",
            options: backendShips.map(s => ({ value: s.id, label: s.ship_name })),
          },
          {
            key: "status",
            label: "Status",
            type: "select",
            placeholder: "All Statuses",
            options: [
              { value: "Open", label: "Open" },
              { value: "Closed", label: "Closed" },
              { value: "Cancelled", label: "Cancelled" },
            ],
          },
          {
            key: "request_date_from",
            label: "Request Date From",
            type: "date",
          },
          {
            key: "request_date_to",
            label: "Request Date To",
            type: "date",
          },
        ]}
        values={jobOrderFilters}
        onValuesChange={setJobOrderFilters}
        onApply={handleApplyJobOrderFilters}
        onReset={handleResetJobOrderFilters}
        scale={scale}
      /> */}

      {/* {showJobOrderModal && (
        <JobOrderFormModal
          jobOrder={selectedJobOrder}
          onClose={() => setShowJobOrderModal(false)}
          onSave={handleSaveJobOrder}
          scale={scale}
        />
      )} */}

      {/* {showRankModal && (
        <RankFormModal
          rank={selectedRank}
          onClose={() => setShowRankModal(false)}
          onSave={handleSaveRank}
          scale={scale}
        />
      )} */}

      <CrewManagementModal
        isOpen={showCrewModal}
        onClose={() => setShowCrewModal(false)}
        ship={targetShipForCrew}
        scale={scale}
      />

      {/* Job Order Management Modal */}
      <JobOrderManagementModal
        isOpen={showJobOrderModal}
        onClose={() => setShowJobOrderModal(false)}
        company={targetCompanyForJobOrder}
        scale={scale}
      />
      {/* Company View Modal */}
      <CompanyViewModal
        isOpen={showCompanyViewModal}
        onClose={() => {
          setShowCompanyViewModal(false);
          setViewingCompany(null);
        }}
        company={viewingCompany}
        onDelete={(id) => {
          setShowCompanyViewModal(false);
          setViewingCompany(null);
          handleDeleteCompany(id);
        }}
        scale={scale}
        canDelete={canDelete}
      />

      {/* Ship View Modal */}
      <ShipViewModal
        isOpen={showShipViewModal}
        onClose={() => {
          setShowShipViewModal(false);
          setViewingShip(null);
        }}
        ship={viewingShip}
        onDelete={(id) => {
          setShowShipViewModal(false);
          setViewingShip(null);
          handleDeleteShip(id);
        }}
        onManageCrew={handleManageCrew}
        scale={scale}
        canDelete={canDelete}
      />
      <ConfirmDialog
        isOpen={showDeleteConfirm}
        onClose={() => {
          setShowDeleteConfirm(false);
          setItemToDelete(null);
          setDeleteType(null);
        }}
        onConfirm={handleConfirmDelete}
        title={`Delete ${deleteType ? deleteType.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') : 'Item'}`}
        message={`Are you sure you want to delete this ${deleteType ? deleteType.replace('_', ' ') : 'item'}? This action cannot be undone.`}
        confirmLabel="Delete"
        variant="danger"
        scale={scale}
        loading={companiesLoading || shipsLoading || jobOrdersLoading || ranksLoading}
      />
    </main>
  );
}
