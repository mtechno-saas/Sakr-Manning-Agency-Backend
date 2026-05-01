
import { mapBackendToFrontend, mapFormToBackend } from './formMapper.js';

const mockBackendUser = {
    // ... basic info ...
    first_name: "Latifah",

    // Sea Services Test (Standard snake_case)
    sea_services: [
        {
            id: 1,
            company_name: "Test Co",
            rank: "Master",
            vessel_name_imo: "Titanic",
            engine_type_bh_kw: "Steam / 50000",
            reason_for_sign_off: "Iceberg"
        }
    ],

    // Documents Test (Standard snake_case)
    documents: [
        {
            id: 101,
            ticket_number: "A1234567",
            type: "passport",
            issuing_authority: "EGY"
        }
    ],

    // Casing Test (PascalCase) mimicking potential backend mismatch
    Courses: [
        {
            id: 501,
            course_name: "Survival",
            number: "123"
        }
    ]
};

console.log("--- Testing Backend -> Frontend (CRUD) ---");
const frontend = mapBackendToFrontend(mockBackendUser);
console.log("Sea Services:", JSON.stringify(frontend.seaServices, null, 2));
console.log("Documents:", JSON.stringify(frontend.documents, null, 2));
console.log("Courses (from PascalCase):", JSON.stringify(frontend.courses, null, 2));

// Verify Splits
const sea = frontend.seaServices[0];
if (sea.engineType !== "Steam") console.error("FAIL: Engine Type split failed");
if (sea.bhKw !== "50000") console.error("FAIL: BH KW split failed");
if (sea.vesselName !== "Titanic") console.error("FAIL: Vessel Name mapping failed");

const doc = frontend.documents[0];
if (doc.documentNo !== "A1234567") console.error("FAIL: Document Number mapping failed");
if (doc.documentType !== "passport") console.error("FAIL: Document Type mapping failed");

const course = frontend.courses[0];
if (!course || course.courseName !== "Survival") console.error("FAIL: PascalCase fallback for Courses failed");


console.log("\n--- Testing Frontend -> Backend (CRUD) ---");
// Create mock frontend data to test combination
const mockFrontendForm = {
    seaServices: [
        {
            companyName: "New Co",
            rank: "Chief Officer",
            vesselName: "Queen Mary",
            engineType: "Diesel",
            bhKw: "20000"
        }
    ],
    documents: [
        {
            documentType: "seamanBook",
            documentNo: "SB999"
        }
    ]
};

const backend = mapFormToBackend(mockFrontendForm);
console.log("Sea Services:", JSON.stringify(backend.sea_services, null, 2));
console.log("Documents:", JSON.stringify(backend.documents, null, 2));

// Verify Combination
const seaBack = backend.sea_services[0];
if (seaBack.engine_type_bh_kw !== "Diesel / 20000") console.error("FAIL: Engine/KW combination failed");
if (seaBack.vessel_name_imo !== "Queen Mary") console.error("FAIL: Vessel Name backend mapping failed");

const docBack = backend.documents[0];
if (docBack.ticket_number !== "SB999") console.error("FAIL: Ticket Number backend mapping failed");
if (docBack.type !== "seamanBook") console.error("FAIL: Document Type backend mapping failed");
