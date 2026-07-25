/* eslint-disable no-unused-vars */

// Content/Principal.jsx - COMPLETE with All Features from CV.jsx
import React, { useState, useEffect, useMemo, useCallback, useRef } from "react";
import { AdvancedDataTable } from "../Components/Data/AdvancedDataTable";
import { DataTableLayout } from "../Components/Data/DataTableLayout";
import { BulkActionBar } from "../Components/Data/BulkActionBar";
import { StatCard } from "../Components/Cards/StatCard";
import { generateStatPdfReport } from "../../../utils/pdfReportGenerator";
import Pagination from "../../common/Pagination";
import { ASSETS } from "../../../utils/constants";
import { COLORS } from "../Constants";
import { Building, Anchor, CheckCircle2, XCircle, Clock, Trash2, Edit, Eye, Download, Briefcase, Users, ChevronDown, ChevronUp, Layers } from "lucide-react";

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

export function CompanyManagement({ scale = 1, isMobile = false, initialItemData }) {
  const { notify } = useNotification();
  const { canCreate, canEdit, canDelete } = usePermissions();

  const {
    companies: backendCompanies,
    loading: companiesLoading,
    fetchCompanies, getCompanyById,
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
  const [selectedJobOrder, setSelectedJobOrder] = useState(null);

  // Section expand states
  const [isCompaniesExpanded, setIsCompaniesExpanded] = useState(true);
  const [isShipsExpanded, setIsShipsExpanded] = useState(true);
  // Single Deletion
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [itemToDelete, setItemToDelete] = useState(null);
  const [deleteType, setDeleteType] = useState(null); // 'company', 'ship', 'job_order', 'rank'

  const [companyStats, setCompanyStats] = useState(null);

  // Bulk Selection State
  const [selectedCompanyIds, setSelectedCompanyIds] = useState([]);
  const [selectedShipIds, setSelectedShipIds] = useState([]);
  const [showCompanyBulkDelete, setShowCompanyBulkDelete] = useState(false);
  const [showShipBulkDelete, setShowShipBulkDelete] = useState(false);

  // Column Visibility state
  const [hiddenCompanyCols, setHiddenCompanyCols] = useState([
    "hourRate", "createdAt", "website", "email", 
    "phone", "address", "country", "contact_person", "contact_person_email", "contact_person_phone", "contact_phone", "owner", "notes", "open_positions", "tax_id", "registration_number", "company_group"
  ]);
  const [showCompanyColPicker, setShowCompanyColPicker] = useState(false);
  const [hiddenShipCols, setHiddenShipCols] = useState([
    "grossTonnage", "deadweight", "engineType", "yearBuilt", "enginePower", "officialNo",
    "call_sign", "mmsi_no", "port_of_registry", "builder", "created_at", "updated_at", "vessel_manager", "engine_make", "engine_model"
  ]);
  const [showShipColPicker, setShowShipColPicker] = useState(false);

  // Filter state for Principals
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

  // Filter state for Vessels
  const [showShipFilterModal, setShowShipFilterModal] = useState(false);
  const [shipFilters, setShipFilters] = useState({
    name: "",
    imo_number: "",
    company: "",
    status: "",
    ship_type: "",
  });
  const [activeShipFilters, setActiveShipFilters] = useState({
    name: "",
    imo_number: "",
    company: "",
    status: "",
    ship_type: "",
  });

  // ✅ NEW: Saved filter presets for both companies and ships
  const [savedCompanyPresets, setSavedCompanyPresets] = useState([]);
  const [savedShipPresets, setSavedShipPresets] = useState([]);

    // Load company statistics
  const loadCompanyStats = useCallback(async () => {
    const result = await fetchCompanyStats();
    if (result.success) {
      setCompanyStats(result.data);
    }
  }, [fetchCompanyStats]);

  // Load data on mount
  useEffect(() => {
    fetchCompanies();
    fetchShips();
    fetchRanks();
    fetchJobOrders();
    loadCompanyStats();
  }, [fetchCompanies, getCompanyById, fetchShips, fetchRanks, fetchJobOrders, loadCompanyStats]);

  // Handle initial item navigation
  const hasOpenedInitial = useRef(false);
  useEffect(() => {
    if (initialItemData && initialItemData.id && !hasOpenedInitial.current) {
      hasOpenedInitial.current = true;
      const loadAndOpen = async () => {
        try {
          // Check if we already have it in the list (e.g. from a previous fetch)
          let company = (backendCompanies || []).find(c => c.id === initialItemData.id);
          if (!company) {
            // Fetch directly from API
            const result = await getCompanyById(initialItemData.id);
            if (result && result.success) {
              company = result.data;
            }
          }
          
          if (company) {
            setViewingCompany(company);
            setShowCompanyViewModal(true);
          }
        } catch (e) {
          console.log("Could not load initial item in Principals", e);
        }
      };
      loadAndOpen();
    }
  }, [initialItemData, backendCompanies, getCompanyById]);

  // Transform backend companies to match UI format
  const companyData = useMemo(() => {
    return (backendCompanies || []).map((company, index) => ({
      index: (companyPagination.currentPage - 1) * (companyPagination.pageSize || 50) + index + 1,
      id: company.id,
      name: company.company_name,
      companyFlag: company.company_flag_name || company.company_flag || "No Flag",
      type: company.company_type_name || company.company_type || "No Type",
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

  const shipData = useMemo(() => {
    return (backendShips || []).map((ship, index) => {
      const associatedCompany = (backendCompanies || []).find(
        (company) => company.id === ship.company
      );
      const associatedFlags = (flags || []).find((flag) => {
        return flag.id === ship.flag;
      });
      const associatedVesselType = (vesselTypes || []).find(
        (vessel) => vessel.id === ship.ship_type
      );
      const shipIns = {
        index: (shipPagination.currentPage - 1) * (shipPagination.pageSize || 50) + index + 1,
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
  }, [backendCompanies, backendShips, flags, vesselTypes, shipPagination.currentPage, shipPagination.pageSize]);


  // ============================================
  // PRINCIPAL CRUD HANDLERS
  // ============================================
  const handleViewCompany = useCallback(
    (row) => {
      // Find full company object
      const company = (backendCompanies || []).find((c) => c.id === row.id);
      if (company) {
        setViewingCompany(company);
        setShowCompanyViewModal(true);
      } else {
        notify.error("Principal data not found");
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
      const company = (backendCompanies || []).find((c) => c.id === row.id);
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

  const handleDownloadCompany = useCallback(
    (row) => {
      try {
        const allCols = [
          { key: "name", header: "Principal Name" },
          { key: "companyFlag", header: "Country" },
          { key: "type", header: "Type" },
          { key: "openPositions", header: "Jobs" },
          { key: "hourRate", header: "Rate/Hr" },
          { key: "createdAt", header: "Created" },
          { key: "website", header: "Website" },
          { key: "email", header: "Email" },
          { key: "status", header: "Status" },
          { key: "phone", header: "Phone" },
          { key: "address", header: "Address" },
          { key: "country", header: "Country" },
          { key: "contact_person", header: "Contact Person" },
          { key: "contact_person_email", header: "Contact Email" },
          { key: "contact_person_phone", header: "Contact Phone" },
          { key: "contact_phone", header: "Alt Phone" },
          { key: "owner", header: "Owner" },
          { key: "notes", header: "Notes" },
          { key: "open_positions", header: "Open Positions" }
        ];
        const pdfCols = allCols.filter(c => !hiddenCompanyCols.includes(c.key));
        generateStatPdfReport(`Company_${row.name ? row.name.replace(/\s+/g, "_") : "Details"}`, pdfCols, [row]);
        notify.success("Principal details downloaded as PDF!");
      } catch (error) {
        notify.error("Failed to download PDF");
        console.error(error);
      }
    },
    [notify, hiddenCompanyCols]
  );

  // ============================================
  // VESSEL CRUD HANDLERS
  // ============================================
  const handleViewShip = useCallback(
    (row) => {
      const ship = (backendShips || []).find((s) => s.id === row.id);
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
        notify.error("Vessel data not found");
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
      const ship = (backendShips || []).find((s) => s.id === row.id);
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
      const jo = (backendJobOrders || []).find((j) => j.id === row.id);
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
      notify.success(`${deleteType.charAt(0).toUpperCase() + deleteType.slice(1).replace("_", " ")} deleted successfully`);
      setShowDeleteConfirm(false);
      setItemToDelete(null);
      setDeleteType(null);
    }
  }, [itemToDelete, deleteType, deleteCompany, deleteShip, deleteJobOrder, deleteRank, loadCompanyStats]);

  const handleBulkDeleteCompanies = useCallback(async () => {
    if (!canDelete) return;
    let successCount = 0;
    for (const id of selectedCompanyIds) {
      const res = await deleteCompany(id);
      if (res && res.success) successCount++;
    }
    notify.success(`Successfully deleted ${successCount} companies.`);
    setSelectedCompanyIds([]);
    setShowCompanyBulkDelete(false);
    await loadCompanyStats();
  }, [canDelete, selectedCompanyIds, deleteCompany, loadCompanyStats, notify]);

  const handleBulkDeleteShips = useCallback(async () => {
    if (!canDelete) return;
    let successCount = 0;
    for (const id of selectedShipIds) {
      const res = await deleteShip(id);
      if (res && res.success) successCount++;
    }
    notify.success(`Successfully deleted ${successCount} ships.`);
    setSelectedShipIds([]);
    setShowShipBulkDelete(false);
  }, [canDelete, selectedShipIds, deleteShip, notify]);

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

  //  // o. NEW: Download individual ship
  const handleDownloadShip = useCallback(
    (row) => {
      try {
        const allCols = [
          { key: "name", header: "Vessel Name" },
          { key: "imoNumber", header: "IMO No" },
          { key: "flag", header: "Flag" },
          { key: "type", header: "Type" },
          { key: "company", header: "Principal" },
          { key: "crewCount", header: "Crew" },
          { key: "grossTonnage", header: "GT" },
          { key: "deadweight", header: "DWT" },
          { key: "engineType", header: "Engine" },
          { key: "yearBuilt", header: "Year Built" },
          { key: "enginePower", header: "Power (KW)" },
          { key: "officialNo", header: "Official No" },
          { key: "status", header: "Status" },
          { key: "call_sign", header: "Call Sign" },
          { key: "mmsi_no", header: "MMSI No" },
          { key: "port_of_registry", header: "Port of Registry" },
          { key: "builder", header: "Builder" },
          { key: "created_at", header: "Created At" },
          { key: "updated_at", header: "Updated At" }
        ];
        const pdfCols = allCols.filter(c => !hiddenShipCols.includes(c.key));
        generateStatPdfReport(`Ship_${row.name ? row.name.replace(/\s+/g, "_") : "Details"}`, pdfCols, [row]);
        notify.success("Vessel details downloaded as PDF!");
      } catch (error) {
        notify.error("Failed to download PDF");
        console.error(error);
      }
    },
    [notify, hiddenShipCols]
  );

  // ✅ Backend Filter Handlers for Principals
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

  // ✅ Backend Filter Handlers for Vessels
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
      ship_type: "",
    };
    setShipFilters(emptyFilters);
    setActiveShipFilters(emptyFilters);
    setShowShipFilterModal(false);
    fetchShips({ page: 1 });
  }, [fetchShips]);

  // Handle page changes
  const handleCompanyPageChange = useCallback((newPage) => {
    fetchCompanies({ ...activeCompanyFilters, page: newPage });
  }, [fetchCompanies, getCompanyById, activeCompanyFilters]);

  // Handle ship page changes
  const handleShipPageChange = useCallback(
    (newPage) => {
      fetchShips({ ...activeShipFilters, page: newPage });
    },
    [fetchShips, activeShipFilters]
  );

  // o. NEW: Export handlers - UPDATED to use backend data
  const handleExportCompaniesExcel = useCallback(() => {
    try {
      const allCols = [
        { key: "name", header: "Principal Name" },
        { key: "companyFlag", header: "Country" },
        { key: "type", header: "Type" },
        { key: "openPositions", header: "Jobs" },
        { key: "hourRate", header: "Rate/Hr" },
        { key: "createdAt", header: "Created" },
        { key: "website", header: "Website" },
        { key: "email", header: "Email" },
        { key: "status", header: "Status" },
        { key: "phone", header: "Phone" },
        { key: "address", header: "Address" },
        { key: "country", header: "Country" },
        { key: "contact_person", header: "Contact Person" },
        { key: "contact_person_email", header: "Contact Email" },
        { key: "contact_person_phone", header: "Contact Phone" },
        { key: "contact_phone", header: "Alt Phone" },
        { key: "owner", header: "Owner" },
        { key: "notes", header: "Notes" },
        { key: "open_positions", header: "Open Positions" }
      ];
      const visibleKeys = allCols.filter(c => !hiddenCompanyCols.includes(c.key)).map(c => c.key);
      const dataToExport = companyData.map(row => {
        const rowData = {};
        visibleKeys.forEach(k => rowData[k] = row[k]);
        return rowData;
      });
      exportToExcel(
        dataToExport,
        `Companies_Export_${new Date().toISOString().split("T")[0]}.xlsx`,
        "Principals"
      );
      notify.success("Principals exported to Excel!");
    } catch (error) {
      notify.error("Failed to export");
    }
  }, [companyData, notify, hiddenCompanyCols]);

  const handleExportCompaniesPdf = useCallback(() => {
    try {
      const allCols = [
        { key: "name", header: "Principal Name" },
        { key: "companyFlag", header: "Country" },
        { key: "type", header: "Type" },
        { key: "openPositions", header: "Jobs" },
        { key: "hourRate", header: "Rate/Hr" },
        { key: "createdAt", header: "Created" },
        { key: "website", header: "Website" },
        { key: "email", header: "Email" },
        { key: "status", header: "Status" },
        { key: "phone", header: "Phone" },
        { key: "address", header: "Address" },
        { key: "country", header: "Country" },
        { key: "contact_person", header: "Contact Person" },
        { key: "contact_person_email", header: "Contact Email" },
        { key: "contact_person_phone", header: "Contact Phone" },
        { key: "contact_phone", header: "Alt Phone" },
        { key: "owner", header: "Owner" },
        { key: "notes", header: "Notes" },
        { key: "open_positions", header: "Open Positions" }
      ];
      const pdfCols = allCols.filter(c => !hiddenCompanyCols.includes(c.key));
      generateStatPdfReport(`Companies_Export`, pdfCols, companyData);
      notify.success("Principals exported to PDF!");
    } catch (error) {
      notify.error("Failed to export PDF");
    }
  }, [companyData, notify, hiddenCompanyCols]);

  const handleExportShipsExcel = useCallback(() => {
    try {
      const allCols = [
        { key: "name", header: "Vessel Name" },
        { key: "imoNumber", header: "IMO No" },
        { key: "flag", header: "Flag" },
        { key: "type", header: "Type" },
        { key: "company", header: "Principal" },
        { key: "crewCount", header: "Crew" },
        { key: "grossTonnage", header: "GT" },
        { key: "deadweight", header: "DWT" },
        { key: "engineType", header: "Engine" },
        { key: "yearBuilt", header: "Year Built" },
        { key: "enginePower", header: "Power (KW)" },
        { key: "officialNo", header: "Official No" },
        { key: "status", header: "Status" },
        { key: "call_sign", header: "Call Sign" },
        { key: "mmsi_no", header: "MMSI No" },
        { key: "port_of_registry", header: "Port of Registry" },
        { key: "builder", header: "Builder" },
        { key: "created_at", header: "Created At" },
        { key: "updated_at", header: "Updated At" }
      ];
      const visibleKeys = allCols.filter(c => !hiddenShipCols.includes(c.key)).map(c => c.key);
      const dataToExport = shipData.map(row => {
        const rowData = {};
        visibleKeys.forEach(k => rowData[k] = row[k]);
        return rowData;
      });
      exportToExcel(
        dataToExport,
        `Ships_Export_${new Date().toISOString().split("T")[0]}.xlsx`,
        "Vessels"
      );
      notify.success("Vessels exported to Excel!");
    } catch (error) {
      notify.error("Failed to export");
    }
  }, [shipData, notify, hiddenShipCols]);

  const handleExportShipsPdf = useCallback(() => {
    try {
      const allCols = [
        { key: "name", header: "Vessel Name" },
        { key: "imoNumber", header: "IMO No" },
        { key: "flag", header: "Flag" },
        { key: "type", header: "Type" },
        { key: "company", header: "Principal" },
        { key: "crewCount", header: "Crew" },
        { key: "grossTonnage", header: "GT" },
        { key: "deadweight", header: "DWT" },
        { key: "engineType", header: "Engine" },
        { key: "yearBuilt", header: "Year Built" },
        { key: "enginePower", header: "Power (KW)" },
        { key: "officialNo", header: "Official No" },
        { key: "status", header: "Status" },
        { key: "call_sign", header: "Call Sign" },
        { key: "mmsi_no", header: "MMSI No" },
        { key: "port_of_registry", header: "Port of Registry" },
        { key: "builder", header: "Builder" },
        { key: "created_at", header: "Created At" },
        { key: "updated_at", header: "Updated At" }
      ];
      const pdfCols = allCols.filter(c => !hiddenShipCols.includes(c.key));
      generateStatPdfReport(`Ships_Export`, pdfCols, shipData);
      notify.success("Vessels exported to PDF!");
    } catch (error) {
      notify.error("Failed to export PDF");
    }
  }, [shipData, notify, hiddenShipCols]);

  const handleRefreshCompanies = useCallback(() => {
    fetchCompanies({ ...activeCompanyFilters, page: 1 });
  }, [fetchCompanies, getCompanyById, activeCompanyFilters]);

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

  const getStatusBadge = useCallback((status) => {
    let bgColor = "bg-slate-100 dark:bg-slate-800/50";
    let textColor = "text-slate-600 dark:text-slate-400";
    
    if (!status) return <span className={`px-2.5 py-1 text-[11px] uppercase tracking-wider font-bold rounded-full ${bgColor} ${textColor}`}>Unknown</span>;
    
    const lower = status.toLowerCase();
    if (lower === "active" || lower === "approved" || lower === "operating") {
      bgColor = "bg-emerald-100 dark:bg-emerald-500/20 border border-emerald-200 dark:border-emerald-500/30";
      textColor = "text-emerald-700 dark:text-emerald-400";
    } else if (lower === "inactive" || lower === "rejected" || lower === "dormant") {
      bgColor = "bg-rose-100 dark:bg-rose-500/20 border border-rose-200 dark:border-rose-500/30";
      textColor = "text-rose-700 dark:text-rose-400";
    } else if (lower === "prospect" || lower === "pending") {
      bgColor = "bg-blue-100 dark:bg-blue-500/20 border border-blue-200 dark:border-blue-500/30";
      textColor = "text-blue-700 dark:text-blue-400";
    } else if (lower === "under maintenance" || lower === "repairing") {
      bgColor = "bg-amber-100 dark:bg-amber-500/20 border border-amber-200 dark:border-amber-500/30";
      textColor = "text-amber-700 dark:text-amber-400";
    }
    
    return (
      <span className={`px-2.5 py-1 text-[11px] uppercase tracking-wider font-bold rounded-full ${bgColor} ${textColor}`}>
        {status}
      </span>
    );
  }, []);

  // Table columns
  const companyColumns = useMemo(
    () => [
      {
        key: "index",
        label: "#",
        width: 60,
        sortable: false,
        render: (val) => val,
      },
      {
        key: "name",
        label: "Principal Name",
        width: 360,
        showAvatar: true,
        sortable: true,
        render: (value, row) => row.name,
      },
      {
        key: "companyFlag",
        label: "Country",
        width: 150,
        sortable: true,
        render: (value) => value || "—",
      },
      {
        key: "type",
        label: "Type",
        width: 350,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "openPositions",
        label: "Jobs",
        width: 80,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "hourRate",
        label: "Rate/Hr",
        width: 100,
        sortable: true,
        render: (value) => `$${value}`,
      },
      {
        key: "createdAt",
        label: "Created",
        width: 120,
        sortable: true,
        render: (value) => {
          if (value === "N/A") return "—";
          return new Date(value).toLocaleDateString();
        }
      },
      {
        key: "website",
        label: "Website",
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
        label: "Email",
        width: 250,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "status",
        label: "Status",
        width: 120,
        sortable: true,
        isStatus: true,
        headerAlign: "center",
        headerTextAlign: "center",
        render: (value) => getStatusBadge(value),
      },
      { key: "phone", label: "Phone", width: 140, sortable: true, render: (_, row) => row.phone || "-" },
      { key: "address", label: "Address", width: 200, sortable: true, render: (_, row) => <div className="truncate max-w-[150px]" title={row.address}>{row.address || "-"}</div> },
      { key: "country", label: "Country", width: 120, sortable: true, render: (_, row) => row.country || "-" },
      { key: "contact_person", label: "Contact Person", width: 150, sortable: true, render: (_, row) => row.contact_person || "-" },
      { key: "contact_person_email", label: "Contact Email", width: 180, sortable: true, render: (_, row) => row.contact_person_email || "-" },
      { key: "contact_person_phone", label: "Contact Phone", width: 140, sortable: true, render: (_, row) => row.contact_person_phone || "-" },
      { key: "contact_phone", label: "Alt Phone", width: 140, sortable: true, render: (_, row) => row.contact_phone || "-" },
      { key: "owner", label: "Owner", width: 150, sortable: true, render: (_, row) => row.owner || "-" },
      { key: "notes", label: "Notes", width: 200, sortable: false, render: (_, row) => <div className="truncate max-w-[150px]" title={row.notes}>{row.notes || "-"}</div> },
      { key: "open_positions", label: "Open Positions", width: 120, sortable: true, render: (_, row) => row.open_positions || "0" },
      {
        key: "actions",
        label: "Actions",
        width: 170,
        render: (_, row) => (
          <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button onClick={(e) => { e.stopPropagation(); handleViewCompany(row); }} className="p-1.5 text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/30" title="View Profile"><Eye size={16} /></button>
            <button onClick={(e) => { e.stopPropagation(); handleDownloadCompany(row); }} className="p-1.5 text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors rounded-lg hover:bg-emerald-50 dark:hover:bg-emerald-900/30" title="Download"><Download size={16} /></button>
            {canEdit && <button onClick={(e) => { e.stopPropagation(); handleManageJobOrders(row); }} className="p-1.5 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-900/30" title="Manage Vacancies"><Briefcase size={16} /></button>}
            {canEdit && <button onClick={(e) => { e.stopPropagation(); handleEditCompany(row); }} className="p-1.5 text-slate-400 hover:text-amber-600 dark:hover:text-amber-400 transition-colors rounded-lg hover:bg-amber-50 dark:hover:bg-amber-900/30" title="Edit"><Edit size={16} /></button>}
            {canDelete && <button onClick={(e) => { e.stopPropagation(); handleDeleteCompany(row.id); }} className="p-1.5 text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 transition-colors rounded-lg hover:bg-rose-50 dark:hover:bg-rose-900/30" title="Delete"><Trash2 size={16} /></button>}
          </div>
        )
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
        key: "index",
        label: "#",
        width: 100, // Increased for more space between index and name
        sortable: false,
        render: (val) => val,
      },
      {
        key: "name",
        label: "Vessel Name",
        width: 400,
        showAvatar: true,
        sortable: true,
        render: (value, row) => row.name,
      },
      {
        key: "imoNumber",
        label: "IMO Number",
        width: 120,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "flag",
        label: "Flag",
        width: 120,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "type",
        label: "Type",
        width: 200,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "associatedWithCompany",
        label: "Principal",
        width: 300,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "jobOrdersCount",
        label: "Jobs",
        width: 80,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "crewCount",
        label: "Crew",
        width: 80,
        sortable: true,
        render: (value) => value,
      },
      {
        key: "grossTonnage",
        label: "GT",
        width: 80,
        sortable: true,
        render: (v) => v,
      },
      {
        key: "deadweight",
        label: "DWT",
        width: 80,
        sortable: true,
        render: (v) => v,
      },
      {
        key: "engineType",
        label: "Engine",
        width: 120,
        sortable: true,
        render: (v) => v,
      },
      {
        key: "yearBuilt",
        label: "Year",
        width: 80,
        sortable: true,
        render: (v) => v,
      },
      {
        key: "enginePower",
        label: "Power",
        width: 100,
        sortable: true,
        render: (v) => `${v} kW`,
      },
      {
        key: "officialNo",
        label: "Official No",
        width: 120,
        sortable: true,
        render: (v) => v,
      },
      {
        key: "status",
        label: "Status",
        width: 120,
        sortable: true,
        isStatus: true,
        headerAlign: "center",
        headerTextAlign: "center",
        render: (value) => getStatusBadge(value),
      },
      { key: "call_sign", label: "Call Sign", width: 120, sortable: true, render: (_, row) => row.call_sign || "-" },
      { key: "mmsi_no", label: "MMSI No", width: 140, sortable: true, render: (_, row) => row.mmsi_no || "-" },
      { key: "port_of_registry", label: "Port of Registry", width: 160, sortable: true, render: (_, row) => row.port_of_registry || "-" },
      { key: "builder", label: "Builder", width: 160, sortable: true, render: (_, row) => row.builder || "-" },
      { key: "created_at", label: "Created At", width: 140, sortable: true, render: (_, row) => row.created_at ? new Date(row.created_at).toLocaleDateString() : "-" },
      { key: "updated_at", label: "Updated At", width: 140, sortable: true, render: (_, row) => row.updated_at ? new Date(row.updated_at).toLocaleDateString() : "-" },
      {
        key: "actions",
        label: "Actions",
        width: 170, // Increased for crew action
        render: (_, row) => (
          <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button onClick={(e) => { e.stopPropagation(); handleViewShip(row); }} className="p-1.5 text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/30" title="View Vessel"><Eye size={16} /></button>
            <button onClick={(e) => { e.stopPropagation(); handleDownloadShip(row); }} className="p-1.5 text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors rounded-lg hover:bg-emerald-50 dark:hover:bg-emerald-900/30" title="Download"><Download size={16} /></button>
            <button onClick={(e) => { e.stopPropagation(); handleManageCrew(row); }} className="p-1.5 text-slate-400 hover:text-purple-600 dark:hover:text-purple-400 transition-colors rounded-lg hover:bg-purple-50 dark:hover:bg-purple-900/30" title="Manage Crew"><Users size={16} /></button>
            {canEdit && <button onClick={(e) => { e.stopPropagation(); handleEditShip(row); }} className="p-1.5 text-slate-400 hover:text-amber-600 dark:hover:text-amber-400 transition-colors rounded-lg hover:bg-amber-50 dark:hover:bg-amber-900/30" title="Edit"><Edit size={16} /></button>}
            {canDelete && <button onClick={(e) => { e.stopPropagation(); handleDeleteShip(row.id); }} className="p-1.5 text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 transition-colors rounded-lg hover:bg-rose-50 dark:hover:bg-rose-900/30" title="Delete"><Trash2 size={16} /></button>}
          </div>
        )
      },
    ],
    [canEdit, canDelete, handleDeleteShip, handleEditShip, handleDownloadShip, handleViewShip, handleManageCrew]
  );

  // Ranks table columns
  const rankColumns = useMemo(
    () => [
      {
        key: "rank_name",
        label: "Rank Name",
        width: 250,
        sortable: true,
        render: (v) => v,
      },
      {
        key: "rank_code",
        label: "Code",
        width: 150,
        sortable: true,
        render: (v) => v,
      },
      {
        key: "actions",
        label: "Actions",
        width: 100,
        render: (_, row) => (
          <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            {canEdit && <button onClick={(e) => { e.stopPropagation(); handleEditRank(row); }} className="p-1.5 text-slate-400 hover:text-amber-600 dark:hover:text-amber-400 transition-colors rounded-lg hover:bg-amber-50 dark:hover:bg-amber-900/30" title="Edit"><Edit size={16} /></button>}
            {canDelete && <button onClick={(e) => { e.stopPropagation(); handleDeleteRank(row.id); }} className="p-1.5 text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 transition-colors rounded-lg hover:bg-rose-50 dark:hover:bg-rose-900/30" title="Delete"><Trash2 size={16} /></button>}
          </div>
        )
      },
    ],
    [canEdit, canDelete, handleEditRank, handleDeleteRank]
  );

  // ✅ NEW: Enhanced filter fields aligned with BE documentation
  const companyFilterFields = [
    {
      key: "name",
      label: "Principal Name",
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
      label: "Principal Type",
      type: "select",
      placeholder: "All Types",
      options: [
        { value: "Shipping Manning Principals", label: "Shipping Manning Principals" },
        { value: "Cargo Manning Principals", label: "Cargo Manning Principals" },
        { value: "Cruise & Hospitality Manning Principals", label: "Cruise & Hospitality Manning Principals" },
        { value: "Offshore & Oil/Gas Manning Principals", label: "Offshore & Oil/Gas Manning Principals" },
        { value: "Fishing Fleet Manning Principals", label: "Fishing Fleet Manning Principals" },
        { value: "General Crew Manning Principals", label: "General Crew Manning Principals" },
        { value: "Specialized Marine Manning Principals", label: "Specialized Marine Manning Principals" },
        { value: "Temporary / Contract Manning Agencies", label: "Temporary / Contract Manning Agencies" },
        { value: "Full Crew Management Principals", label: "Full Crew Management Principals" },
      ],
    },
  ];

  const shipFilterFields = [
    {
      key: "name",
      label: "Vessel Name",
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
      label: "Principal",
      type: "select",
      multiple: true,
      placeholder: "All Principals",
      options: (referenceOptions?.companies || []),
    },
    {
      key: "status",
      label: "Status",
      type: "select",
      multiple: true,
      placeholder: "All Statuses",
      options: [
        { value: "Active", label: "Active" },
        { value: "Under Maintenance", label: "Under Maintenance" },
        { value: "Inactive", label: "Inactive" },
      ],
    },
    {
      key: "ship_type",
      label: "Vessel Type",
      type: "select",
      multiple: true,
      placeholder: "All Types",
      options: [
        { value: "Container Vessels", label: "Container Vessels" },
        { value: "Bulk Carriers", label: "Bulk Carriers" },
        { value: "Tankers", label: "Tankers" },
        { value: "Ro-Ro Vessels", label: "Ro-Ro Vessels" },
        { value: "Passenger Vessels", label: "Passenger Vessels" },
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
    return (backendJobOrders || []).map((jo) => {
      const company = (backendCompanies || []).find((c) => c.id === jo.company);
      const ship = (backendShips || []).find((s) => s.id === jo.ship);
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
  //       title: "Principal",
  //       width: 180,
  //       sortable: true,
  //       render: (v) => v,
  //     },
  //     {
  //       key: "shipName",
  //       title: "Vessel",
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

  // ── Statistics ──
  const companyStatistics = useMemo(() => {
    const counts = companyData.reduce((acc, item) => {
      acc[item.status] = (acc[item.status] || 0) + 1;
      acc.total += 1;
      return acc;
    }, { total: 0 });

    const cols = [
      { key: "name", header: "Principal Name" },
      { key: "type", header: "Type" },
      { key: "email", header: "Email" },
      { key: "openPositions", header: "Jobs" },
      { key: "status", header: "Status" }
    ];

    return [
      { title: "Total Principals", value: counts.total || 0, trend: "Registered", icon: <Building size={20} />, accent: COLORS.primary || "#1E40AF", onClick: () => generateStatPdfReport("Total Principals", cols, companyData) },
      { title: "Active", value: counts["Active"] || 0, trend: "Operating", icon: <CheckCircle2 size={20} />, accent: "#10B981", onClick: () => generateStatPdfReport("Active Principals", cols, companyData.filter(d => d.status === "Active")) },
      { title: "Inactive", value: counts["Inactive"] || 0, trend: "Dormant", icon: <Clock size={20} />, accent: "#F59E0B", onClick: () => generateStatPdfReport("Inactive Principals", cols, companyData.filter(d => d.status === "Inactive")) },
      { title: "Prospects", value: counts["Prospect"] || 0, trend: "Leads", icon: <Building size={20} />, accent: "#6366F1", onClick: () => generateStatPdfReport("Prospect Principals", cols, companyData.filter(d => d.status === "Prospect")) },
    ];
  }, [companyData]);

  const shipStatistics = useMemo(() => {
    const counts = shipData.reduce((acc, item) => {
      acc[item.status] = (acc[item.status] || 0) + 1;
      acc.total += 1;
      return acc;
    }, { total: 0 });

    const cols = [
      { key: "name", header: "Vessel Name" },
      { key: "imoNumber", header: "IMO" },
      { key: "flag", header: "Flag" },
      { key: "type", header: "Type" },
      { key: "associatedWithCompany", header: "Principal" },
      { key: "status", header: "Status" }
    ];

    return [
      { title: "Total Vessels", value: counts.total || 0, trend: "Fleet Size", icon: <Anchor size={20} />, accent: COLORS.primary || "#1E40AF", onClick: () => generateStatPdfReport("Total Vessels", cols, shipData) },
      { title: "Active", value: counts["Active"] || 0, trend: "In Service", icon: <CheckCircle2 size={20} />, accent: "#10B981", onClick: () => generateStatPdfReport("Active Vessels", cols, shipData.filter(d => d.status === "Active")) },
      { title: "Under Maintenance", value: counts["Under Maintenance"] || 0, trend: "Repairing", icon: <Clock size={20} />, accent: "#F59E0B", onClick: () => generateStatPdfReport("Vessels Under Maintenance", cols, shipData.filter(d => d.status === "Under Maintenance")) },
      { title: "Inactive", value: counts["Inactive"] || 0, trend: "Laid Up", icon: <XCircle size={20} />, accent: "#EF4444", onClick: () => generateStatPdfReport("Inactive Vessels", cols, shipData.filter(d => d.status === "Inactive")) },
    ];
  }, [shipData]);

  const headerHeight = Math.round(80 * scale);

  return (
    <main style={{...getMainContainerStyles(scale, headerHeight), minWidth: 0}}>
      <style>{generateAllPageStyles(scale)}</style>

      {/* Principals Section */}
      <section style={{ marginBottom: `${Math.round(13 * scale)}px` }}>
        <div style={{ ...getRowBetweenStyles(scale), cursor: "pointer", userSelect: "none" }} onClick={() => setIsCompaniesExpanded(!isCompaniesExpanded)} className="group mb-6">
          <div className="flex items-center gap-4">
            <div className="relative flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500/10 to-indigo-500/10 dark:from-blue-400/10 dark:to-indigo-400/10 border border-blue-500/20 group-hover:scale-105 transition-transform">
              <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+PHBhdGggZD0iTTAgNDBsNDAtNDBNMCAwbDQwIDQwIiBzdHJva2U9IiMzYjgyZjYiIHN0cm9rZS13aWR0aD0iMC41IiBvcGFjaXR5PSIwLjIiLz48L3N2Zz4=')] opacity-50 rounded-2xl mix-blend-overlay"></div>
              <Building size={24} className="text-blue-600 dark:text-blue-400 relative z-10" />
            </div>
            <h2 className="font-sans font-extrabold text-2xl tracking-tight text-slate-800 dark:text-slate-100 m-0 group-hover:text-blue-600 transition-colors">
              Principals Overview
            </h2>
            <div className="text-slate-400 group-hover:text-blue-500 transition-colors ml-2">
                {isCompaniesExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </div>
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: `${Math.round(8 * scale)}px`, alignItems: "center" }} onClick={e => e.stopPropagation()}>
            <Button variant="icon" onClick={handleRefreshCompanies} title="Refresh" scale={scale} style={{ width: 30, height: 30, borderRadius: 8, minHeight: 30 }}>
              <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" /><path d="M21 3v5h-5" /><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" /><path d="M8 16H3v5" /></svg>
            </Button>
            {canCreate && <Button variant="primary" onClick={handleAddCompany} scale={scale} style={{ minHeight: 30, height: 30, padding: "0 14px", fontSize: 13, borderRadius: 8, fontWeight: 500 }}>Add Principal</Button>}
            <Button variant="outline" onClick={handleExportCompaniesPdf} scale={scale} style={{ minHeight: 30, height: 30, padding: "0 14px", fontSize: 13, borderRadius: 8, fontWeight: 500 }}>Export PDF</Button>
            <Button variant="outline" onClick={handleExportCompaniesExcel} scale={scale} style={{ minHeight: 30, height: 30, padding: "0 14px", fontSize: 13, borderRadius: 8, fontWeight: 500 }}>Export Excel</Button>
          </div>
        </div>

        {isCompaniesExpanded && (
          <div className="animate-in slide-in-from-top-2 duration-300 origin-top">

        {/* KPIs */}
        <div className="mb-6">
          <div className="flex gap-4 overflow-x-auto pb-4 snap-x snap-mandatory [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
            {companyStatistics.map((stat, index) => (
              <div key={index} className="snap-start flex-shrink-0" title="Click to download PDF report">
                <StatCard 
                  title={stat.title} 
                  value={stat.value} 
                  trend={stat.trend} 
                  icon={stat.icon} 
                  accentColor={stat.accent} 
                  onClick={stat.onClick} 
                />
              </div>
            ))}
          </div>
        </div>

        {/* Bulk Actions */}
        <BulkActionBar
          selectedCount={selectedCompanyIds.length}
          onClearSelection={() => setSelectedCompanyIds([])}
          actions={[
            {
              label: "Delete Selected",
              icon: <Trash2 size={16} />,
              onClick: () => setShowCompanyBulkDelete(true),
              variant: "danger",
            }
          ]}
        />

        {/* Principals Table wrapped in Sidebar Layout */}
        <DataTableLayout
          columns={companyColumns}
          storageKey="companies"
          fields={companyFilterFields}
          filters={activeCompanyFilters}
          onFilterChange={(k, v) => setActiveCompanyFilters(prev => ({ ...prev, [k]: v }))}
          onApplyFilters={() => {
            setCompanyFilters(activeCompanyFilters);
            fetchCompanies({ ...activeCompanyFilters, page: 1 });
          }}
          onClearFilters={() => {
            handleResetCompanyFilters();
          }}
        >
          <AdvancedDataTable
            data={companyData}
            columns={companyColumns}
            keyField="id"
            selectedIds={selectedCompanyIds}
            onSelectionChange={setSelectedCompanyIds}
            onRowClick={(c) => {
              setViewingCompany(c);
              setShowCompanyViewModal(true);
            }}
            isLoading={companiesLoading}
            emptyStateMessage="No companies found."
          />
        </DataTableLayout>

        <div className="mt-4">
          <Pagination
            page={companyPagination.currentPage}
            pageSize={companyPagination.pageSize || 50} // Default page size
            total={companyPagination.count}
            onChange={handleCompanyPageChange}
            scale={scale}
            showInfo={true}
          />
        </div>
        </div>
        )}
      </section>

      {/* Vessels Section */}
      <section>
        <div style={{ ...getRowBetweenStyles(scale), cursor: "pointer", userSelect: "none" }} onClick={() => setIsShipsExpanded(!isShipsExpanded)} className="group mb-6">
          <div className="flex items-center gap-4">
            <div className="relative flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500/10 to-purple-500/10 dark:from-indigo-400/10 dark:to-purple-400/10 border border-indigo-500/20 group-hover:scale-105 transition-transform">
              <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+PHBhdGggZD0iTTAgNDBsNDAtNDBNMCAwbDQwIDQwIiBzdHJva2U9IiMzYjgyZjYiIHN0cm9rZS13aWR0aD0iMC41IiBvcGFjaXR5PSIwLjIiLz48L3N2Zz4=')] opacity-50 rounded-2xl mix-blend-overlay"></div>
              <Anchor size={24} className="text-indigo-600 dark:text-indigo-400 relative z-10" />
            </div>
            <h2 className="font-sans font-extrabold text-2xl tracking-tight text-slate-800 dark:text-slate-100 m-0 group-hover:text-indigo-600 transition-colors">
              Vessels Overview
            </h2>
            <div className="text-slate-400 group-hover:text-indigo-500 transition-colors ml-2">
                {isShipsExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </div>
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: `${Math.round(8 * scale)}px`, alignItems: "center" }} onClick={e => e.stopPropagation()}>
            <Button variant="icon" onClick={handleRefreshShips} title="Refresh" scale={scale} style={{ width: 30, height: 30, borderRadius: 8, minHeight: 30 }}>
              <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" /><path d="M21 3v5h-5" /><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" /><path d="M8 16H3v5" /></svg>
            </Button>
            {canCreate && <Button variant="primary" onClick={handleAddShip} scale={scale} style={{ minHeight: 30, height: 30, padding: "0 14px", fontSize: 13, borderRadius: 8, fontWeight: 500 }}>Add Vessel</Button>}
            {selectedShipIds.length > 0 && canDelete && (
              <Button variant="danger" onClick={() => setShowShipBulkDelete(true)} scale={scale} style={{ minHeight: 30, height: 30, padding: "0 14px", fontSize: 13, borderRadius: 8, fontWeight: 500 }}>Delete ({selectedShipIds.length})</Button>
            )}
            <Button variant="outline" onClick={handleExportShipsPdf} scale={scale} style={{ minHeight: 30, height: 30, padding: "0 14px", fontSize: 13, borderRadius: 8, fontWeight: 500 }}>Export PDF</Button>
            <Button variant="outline" onClick={handleExportShipsExcel} scale={scale} style={{ minHeight: 30, height: 30, padding: "0 14px", fontSize: 13, borderRadius: 8, fontWeight: 500 }}>Export Excel</Button>
          </div>
        </div>

        {isShipsExpanded && (
          <div className="animate-in slide-in-from-top-2 duration-300 origin-top">

        {/* KPIs */}
        <div className="mb-6">
          <div className="flex gap-4 overflow-x-auto pb-4 snap-x snap-mandatory [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
            {shipStatistics.map((stat, index) => (
              <div key={index} className="snap-start flex-shrink-0" title="Click to download PDF report">
                <StatCard 
                  title={stat.title} 
                  value={stat.value} 
                  trend={stat.trend} 
                  icon={stat.icon} 
                  accentColor={stat.accent} 
                  onClick={stat.onClick} 
                />
              </div>
            ))}
          </div>
        </div>

        {/* Bulk Actions */}
        <BulkActionBar
          selectedCount={selectedShipIds.length}
          onClearSelection={() => setSelectedShipIds([])}
          actions={[
            {
              label: "Delete Selected",
              icon: <Trash2 size={16} />,
              onClick: () => setShowShipBulkDelete(true),
              variant: "danger",
            }
          ]}
        />

        {/* Vessels Table wrapped in Sidebar Layout */}
        <DataTableLayout
          columns={shipColumns}
          storageKey="ships"
          fields={shipFilterFields}
          filters={activeShipFilters}
          onFilterChange={(k, v) => setActiveShipFilters(prev => ({ ...prev, [k]: v }))}
          onApplyFilters={() => {
            setShipFilters(activeShipFilters);
            fetchShips({ ...activeShipFilters, page: 1 });
          }}
          onClearFilters={() => {
            handleResetShipFilters();
          }}
        >
          <AdvancedDataTable
            data={shipData}
            columns={shipColumns}
            keyField="id"
            selectedIds={selectedShipIds}
            onSelectionChange={setSelectedShipIds}
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
                  <h4 style={{ margin: 0, marginBottom: Math.round(12 * scale), fontSize: Math.round(14 * scale), fontWeight: 600 }} className="text-blue-600 dark:text-blue-400">Associated Job Orders</h4>
                  <div style={{ display: "flex", flexDirection: "column", gap: Math.round(8 * scale) }}>
                    {shipJobOrders.map(jo => (
                      <div key={jo.id} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700" style={{
                        borderRadius: Math.round(6 * scale),
                        padding: Math.round(12 * scale),
                      }}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: Math.round(8 * scale) }}>
                          <div className="font-medium text-slate-900 dark:text-slate-100" style={{ fontSize: Math.round(13 * scale) }}>Reference: {jo.reference_number || 'N/A'}</div>
                          <div className="text-slate-500 dark:text-slate-400" style={{ fontSize: Math.round(12 * scale) }}>Status: {jo.status || 'Active'}</div>
                        </div>
                        {jo.positions && jo.positions.length > 0 ? (
                          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: Math.round(8 * scale) }}>
                            {jo.positions.map(pos => (
                              <div key={pos.id} className="bg-slate-50 dark:bg-slate-800" style={{ padding: Math.round(8 * scale), borderRadius: Math.round(4 * scale), fontSize: Math.round(12 * scale), display: "flex", flexDirection: "column", gap: Math.round(4 * scale) }}>
                                <div style={{ display: "flex", justifyContent: "space-between" }}>
                                  <span className="font-semibold text-slate-900 dark:text-slate-100">{pos.rank_name || pos.rank || 'N/A'}</span>
                                  <span className="font-medium text-slate-500">Req: {pos.quantity || 1}</span>
                                </div>
                                <div style={{ display: "flex", justifyContent: "space-between", fontSize: Math.round(11 * scale) }}>
                                  <span className="text-emerald-600 dark:text-emerald-400">Signed: {pos.filled_slots || 0}</span>
                                  <span className="text-amber-600 dark:text-amber-400">Rem: {pos.remaining_slots || 0}</span>
                                </div>
                                {pos.assigned_to && pos.assigned_to.length > 0 && (
                                  <div className="text-blue-600 dark:text-blue-400 truncate mt-1" style={{ fontSize: Math.round(11 * scale) }} title={`Assigned: ${pos.assigned_to.join(", ")}`}>
                                    Assigned: {pos.assigned_to.join(", ")}
                                  </div>
                                )}
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
            onRowClick={handleViewShip}
            isLoading={shipsLoading}
            emptyStateMessage="No ships found."
          />
        </DataTableLayout>
        {/* Vessel Pagination */}
        <div className="mt-4">
          <Pagination
            page={shipPagination.currentPage || 1}
            pageSize={shipPagination.pageSize || 50}
            total={shipPagination.count || 0}
            onChange={handleShipPageChange}
            scale={scale}
            showInfo={true}
          />
        </div>
        </div>
        )}
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

      {/* ✅ MODALS - Principals */}
      {/* <EnhancedFilterModel
        isOpen={showCompanyFilterModal}
        onClose={() => setShowCompanyFilterModal(false)}
        title="Filter Principals"
        fields={companyFilterFields}
        values={companyFilters}
        onValuesChange={setCompanyFilters}
        onApply={handleApplyCompanyFilters}
        onReset={handleResetCompanyFilters}
        scale={scale}
      /> */}

      {showCompanyModal && (
        <CompanyFormModal
          company={selectedCompany}
          onClose={() => setShowCompanyModal(false)}
          onSave={handleSaveCompany}
          scale={scale}
        />
      )}

      {/* ✅ MODALS - Vessels */}
      {/* <EnhancedFilterModel
        isOpen={showShipFilterModal}
        onClose={() => setShowShipFilterModal(false)}
        title="Filter Vessels"
        fields={shipFilterFields}
        values={shipFilters}
        onValuesChange={setShipFilters}
        onApply={handleApplyShipFilters}
        onReset={handleResetShipFilters}
        scale={scale}
      /> */}

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
            label: "Principal",
            type: "select",
            placeholder: "All Principals",
            options: (backendCompanies || []).map(c => ({ value: c.id, label: c.company_name })),
          },
          {
            key: "ship_name",
            label: "Vessel Name",
            type: "select",
            placeholder: "All Vessels",
            options: (backendShips || []).map(s => ({ value: s.id, label: s.ship_name })),
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
      {/* Principal View Modal */}
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

      {/* Vessel View Modal */}
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
        isOpen={showCompanyBulkDelete}
        onClose={() => setShowCompanyBulkDelete(false)}
        onConfirm={handleBulkDeleteCompanies}
        title="Delete Selected Principals"
        message={`Are you sure you want to delete ${selectedCompanyIds.length} companies? This action cannot be undone.`}
        confirmLabel="Delete All"
        variant="danger"
        scale={scale}
      />
      <ConfirmDialog
        isOpen={showShipBulkDelete}
        onClose={() => setShowShipBulkDelete(false)}
        onConfirm={handleBulkDeleteShips}
        title="Delete Selected Vessels"
        message={`Are you sure you want to delete ${selectedShipIds.length} ships? This action cannot be undone.`}
        confirmLabel="Delete All"
        variant="danger"
        scale={scale}
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



