// // CVManagement.jsx
// import React, { useState } from "react";
// import { COLORS } from "../Constants";
// import { ASSETS } from "../../../utils/constants";

// import { RefinedDataTable } from "../Components/Data/RefinedDataTable";
// import {
//   StatisticsCard,
//   SmallProgressCard,
//   StackedProgressLegendCard,
// } from "../Components/Cards/StatisticsCards";

// import { InfoCard } from "../Components/Cards/InfoCard";

// /* ---------------------- Example sample data ---------------------- */
// const employees = [
//   {
//     id: "e1",
//     avatar: "/assets/avatars/daniel.jpg",
//     name: "Daniel Wilson",
//     position: "Chief Engineer",
//     experience: 15,
//     submitted: "2025-02-10",
//     status: "Under Review",
//   },
//   {
//     id: "e2",
//     avatar: "/assets/avatars/michael.jpg",
//     name: "Michael Johnson",
//     position: "Navigation Officer",
//     experience: 8,
//     submitted: "2025-02-12",
//     status: "Approved",
//   },
//   {
//     id: "e3",
//     avatar: "/assets/avatars/david.jpg",
//     name: "David Thomas",
//     position: "Marine Engineer",
//     experience: 12,
//     submitted: "2025-02-11",
//     status: "Pending",
//   },
//   {
//     id: "e4",
//     avatar: "/assets/avatars/alex.jpg",
//     name: "Alex Taylor",
//     position: "Deck Officer",
//     experience: 10,
//     submitted: "2025-02-11",
//     status: "Interviewed",
//   },
//   {
//     id: "e5",
//     avatar: "/assets/avatars/jordan.jpg",
//     name: "Jordan White",
//     position: "Marine Engineer",
//     experience: 8,
//     submitted: "2025-02-11",
//     status: "Under Review",
//   },
// ];

// const companies = [
//   {
//     id: "c1",
//     avatar: "/assets/icons/company-1.png",
//     company: "Ocean Maritime Ltd",
//     type: "Shipping",
//     openPositions: 12,
//     email: "john@ocean.com",
//     status: "Active",
//   },
//   {
//     id: "c2",
//     avatar: "/assets/icons/company-2.png",
//     company: "Blue Sea Cruises",
//     type: "Cruise",
//     openPositions: 8,
//     email: "hr@bluesea.com",
//     status: "INACTIVE",
//   },
//   {
//     id: "c3",
//     avatar: "/assets/icons/company-3.png",
//     company: "Global Cargo Corp",
//     type: "Offshore",
//     openPositions: 6,
//     email: "jobs@maritime.com",
//     status: "Active",
//   },
// ];

// const ships = [
//   {
//     id: "s1",
//     avatar: "/assets/icons/ship.png",
//     shipName: "Sara Johnson",
//     email: "sara@maritime.com",
//     role: "Admin",
//     lastLogin: "2024-01-20",
//     status: "Active",
//   },
//   {
//     id: "s2",
//     avatar: "/assets/icons/ship.png",
//     shipName: "Mike Chen",
//     email: "mike@maritime.com",
//     role: "HR Manager",
//     lastLogin: "2024-01-19",
//     status: "Active",
//   },
//   {
//     id: "s3",
//     avatar: "/assets/icons/ship.png",
//     shipName: "Lisa Anderson",
//     email: "lisa@maritime.com",
//     role: "Recruiter",
//     lastLogin: "2024-01-18",
//     status: "Active",
//   },
// ];

// /* ---------------------- Column configurations ---------------------- */
// /* Employee columns (matches second screenshot / Refined frame) */
// const employeeColumns = [
//   {
//     key: "name",
//     title: "Employee Name",
//     width: 230,
//     showAvatar: true,
//     render: (val, row) => row.name,
//   },
//   { key: "position", title: "Position", width: 202 },
//   {
//     key: "experience",
//     title: "Experience",
//     width: 126,
//     render: (v) => `${v} years`,
//   },
//   {
//     key: "submitted",
//     title: "Submitted",
//     width: 107,
//     render: (v) => (v ? new Date(v).toLocaleDateString() : ""),
//   },
//   { key: "status", title: "status", width: 135, isStatus: true },
//   {
//     key: "actions",
//     title: "Actions",
//     width: 111,
//     isActions: true,
//     // optional: custom actions (overrides default edit/delete)
//     render: (row) => (
//       <div style={{ display: "flex", gap: 12 }}>
//         {/* Replace with your own handlers */}
//         <button
//           aria-label="View"
//           title="View"
//           onClick={(e) => {
//             e.stopPropagation();
//             console.log("View", row.id);
//           }}
//         >
//           👤
//         </button>
//         <button
//           aria-label="Download"
//           title="Download"
//           onClick={(e) => {
//             e.stopPropagation();
//             console.log("Download", row.id);
//           }}
//         >
//           ⬇️
//         </button>
//       </div>
//     ),
//   },
// ];

// /* Company columns (matches first screenshot) */
// const companyColumns = [
//   {
//     key: "company",
//     title: "Company Name",
//     width: 230,
//     showAvatar: true,
//     render: (v, row) => row.company,
//   },
//   { key: "type", title: "Type", width: 127 },
//   { key: "openPositions", title: "Open Positions", width: 126 },
//   { key: "email", title: "EMAIL", width: 225 },
//   { key: "status", title: "status", width: 172, isStatus: true },
//   {
//     key: "actions",
//     title: "Actions",
//     width: 132,
//     isActions: true,
//     render: (row) => (
//       <>
//         <button
//           aria-label="Edit"
//           onClick={(e) => {
//             e.stopPropagation();
//             console.log("edit", row.id);
//           }}
//         >
//           ✏️
//         </button>
//         <button
//           aria-label="Delete"
//           onClick={(e) => {
//             e.stopPropagation();
//             console.log("delete", row.id);
//           }}
//         >
//           🗑️
//         </button>
//       </>
//     ),
//   },
// ];

// /* Ships/users columns (third screenshot) */
// const shipColumns = [
//   {
//     key: "shipName",
//     title: "Ship Name",
//     width: 230,
//     showAvatar: true,
//     render: (v, r) => r.shipName,
//   },
//   { key: "email", title: "Email", width: 225 },
//   {
//     key: "role",
//     title: "Role",
//     width: 127,
//     render: (v) => (
//       <span style={{ color: v === "Admin" ? "#A259FF" : "#06A7FF" }}>{v}</span>
//     ),
//   },
//   { key: "lastLogin", title: "Last Login", width: 126, render: (v) => v },
//   { key: "status", title: "status", width: 172, isStatus: true },
//   {
//     key: "actions",
//     title: "Actions",
//     width: 82,
//     isActions: true,
//     render: (row) => (
//       <div style={{ display: "flex", gap: 12 }}>
//         <button
//           aria-label="Edit"
//           onClick={(e) => {
//             e.stopPropagation();
//             console.log("edit", row.id);
//           }}
//         >
//           ✏️
//         </button>
//         <button
//           aria-label="Delete"
//           onClick={(e) => {
//             e.stopPropagation();
//             console.log("delete", row.id);
//           }}
//         >
//           🗑️
//         </button>
//       </div>
//     ),
//   },
// ];

// const segments = [
//   { key: "under", label: "Under review", value: 40, color: "#52C93F" },
//   {
//     key: "interviewed",
//     label: "Total Interviewed",
//     value: 60,
//     color: "#D6B7FF",
//   },
//   { key: "pending", label: "Total Pending", value: 30, color: "#A2A2A2" },
//   { key: "approved", label: "Approved", value: 20, color: "#2477C3" },
// ];

// /* ---------------------- Parent component ---------------------- */
// export function GeneralTemp() {
//   const [mode, setMode] = useState("employees"); // or "companies" / "ships"
//   const [scale, setScale] = useState(1); // control pixel scaling
//   const [pageSize, setPageSize] = useState(5);

//   // const onEdit = (item) => {
//   //   console.log("edit", item);
//   //   // open modal / set form state here
//   // };
//   // const onDelete = (id) => {
//   //   console.log("delete", id);
//   //   // show confirm dialog / call API
//   // };
//   const onRowClick = (row) => {
//     console.log("row click", row);
//     // navigation or selection logic
//   };

//   // Choose dataset & columns based on current mode
//   const dataset =
//     mode === "employees" ? employees : mode === "companies" ? companies : ships;
//   const columns =
//     mode === "employees"
//       ? employeeColumns
//       : mode === "companies"
//       ? companyColumns
//       : shipColumns;

//   return (
//     <div style={{ padding: 20 }}>
//       <div
//         style={{
//           display: "flex",
//           gap: 12,
//           alignItems: "center",
//           marginTop: 102,
//           marginBottom: 16,
//         }}
//       >
//         <button onClick={() => setMode("employees")} style={{ padding: 8 }}>
//           Employees
//         </button>
//         <button onClick={() => setMode("companies")} style={{ padding: 8 }}>
//           Companies
//         </button>
//         <button onClick={() => setMode("ships")} style={{ padding: 8 }}>
//           Ships
//         </button>
//         <div
//           style={{
//             marginLeft: "auto",
//             display: "flex",
//             gap: 12,
//             alignItems: "center",
//           }}
//         >
//           <label style={{ fontSize: 14 }}>Scale:</label>
//           <input
//             type="range"
//             min="0.8"
//             max="1.3"
//             step="0.05"
//             value={scale}
//             onChange={(e) => setScale(Number(e.target.value))}
//           />
//           <span>{scale.toFixed(2)}×</span>

//           <label style={{ marginLeft: 12 }}>Page size:</label>
//           <select
//             value={pageSize}
//             onChange={(e) => setPageSize(Number(e.target.value))}
//           >
//             <option value={3}>3</option>
//             <option value={5}>5</option>
//             <option value={8}>8</option>
//             <option value={10}>10</option>
//           </select>
//         </div>
//       </div>

//       <RefinedDataTable
//         data={dataset}
//         columns={columns}
//         rowKey="id"
//         pageSize={pageSize}
//         initialPage={1}
//         scale={scale}
//         // small style override example: tweak header font or column gap design units
//         styleOverrides={{ headerFontSize: 16, columnGap: 29 }}
//         onRowClick={onRowClick}
//       />

//       <StatisticsCard
//         segments={segments}
//         title="Hire vs Cancel"
//         timeframeLabel="Today"
//         scale={1}
//       />
//       <div style={{ display: "flex", gap: 24, padding: 24 }}>
//         <SmallProgressCard title="Protein" percent={82} scale={1} />
//         <div>
//           <StackedProgressLegendCard
//             segments={[
//               { key: "a", color: "#35C2FD", pct: 60 },
//               { key: "b", color: "#38DA4E", pct: 40 },
//               { key: "c", color: "#BF4DD1", pct: 20 },
//             ]}
//             rows={[
//               {
//                 key: "carbs",
//                 color: "#BF4DD1",
//                 label: "Carbs",
//                 remaining: "Remaining",
//               },
//               {
//                 key: "protein",
//                 color: "#38DA4E",
//                 label: "Protein",
//                 remaining: "Remaining",
//               },
//               {
//                 key: "fat",
//                 color: "#35C2FD",
//                 label: "Fat",
//                 remaining: "Remaining",
//               },
//             ]}
//             scale={1}
//           />
//         </div>
//       </div>

//       <InfoCard
//         variant="default"
//         scale={1}
//         avatar={{ src: "/assets/avatar2.jpg" }}
//         title="John Doe"
//         subtitle="Some Title or Company"
//         actions={[
//           {
//             key: "signup",
//             label: "Sign up",
//             onClick: () => console.log("signup"),
//             style: { background: "#1976D2" },
//           },
//           {
//             key: "add",
//             label: "Add",
//             onClick: () => console.log("add"),
//             style: { background: "#056BB6" },
//           },
//         ]}
//       />

//       <InfoCard
//         variant="default"
//         scale={1}
//         avatar={{ src: "/assets/avatar2.jpg" }}
//         title="John Doe"
//         subtitle="Some Title or Company"
//         actions={[
//           {
//             key: "signup",
//             label: "Sign up",
//             onClick: () => console.log("signup"),
//             style: { background: "#1976D2" },
//           },
//           {
//             key: "add",
//             label: "Add",
//             onClick: () => console.log("add"),
//             style: { background: "#056BB6" },
//           },
//         ]}
//       />

//       <InfoCard
//         variant="wide"
//         scale={1}
//         avatar={{ src: "/assets/avatar3.jpg" }}
//         title="Maria Garcia Navigation Officer Duration: 12 months"
//         subtitle="Generated: 2024-01-18 · Signed: 2024-01-19"
//         actions={[
//           {
//             key: "add",
//             label: "Add",
//             onClick: () => {},
//             style: { background: "#FDFECF", color: "#000" },
//           },
//         ]}
//       />
//     </div>
//   );
// }

/////////////////////////////////////////////////////////////////////////////

// FinanceInlineForm.jsx
import React, { useState } from "react";
import { BaseInput } from "../../form/inputs/BaseInput";
import { Select } from "../../form/inputs/Select";
import { DateInput } from "../../form/inputs/DateInput";
import { COLORS } from "../Constants";

export function FinanceRecords({ scale = 1 }) {
  // page tokens (same approach as Company.jsx)
  const headerHeight = Math.round(101 * scale);
  const contentPadding = Math.round(32 * scale);

  // visual tokens scaled
  const gap = Math.round(28 * scale);
  const labelSize = Math.round(18 * scale);
  const labelLineHeight = Math.round(24 * scale);
  const inputHeight = Math.round(60 * scale);
  const inputWidth = Math.round(616 * Math.min(scale, 1)); // keep sensible max width
  const buttonsGap = Math.round(12 * scale);
  const buttonsTop = Math.round(22 * scale);
  const maxRowWidth = Math.round(1100 * Math.min(scale, 1));

  const [record, setRecord] = useState({
    user: "",
    company: "",
    startDate: "",
    endDate: "",
  });
  const [records, setRecords] = useState([]);

  const COMPANIES = [
    { value: "", label: "Add company" },
    { value: "ocean", label: "Ocean Maritime Ltd" },
    { value: "blue", label: "Blue Sea Cruises" },
    { value: "global", label: "Global Cargo Corp" },
    { value: "maritime", label: "Maritime Solutions" },
  ];

  const handleChange = (field) => (value) =>
    setRecord((r) => ({ ...r, [field]: value }));

  const handleAdd = () => {
    if (!record.user?.trim() || !record.company) {
      window.alert("Please fill User and Company before adding.");
      return;
    }
    const item = { id: Date.now(), ...record };
    setRecords((prev) => {
      const next = [item, ...prev];
      console.log("Added record:", item);
      console.log("Mock records:", next);
      return next;
    });
    setRecord({ user: "", company: "", startDate: "", endDate: "" });
  };

  const handleSave = () => {
    const payload = {
      savedAt: new Date().toISOString(),
      count: records.length,
      records,
    };
    console.log("Save payload (mock):", payload);
    window.alert("Saved (mock) — check console for payload.");
  };

  return (
    <main
      style={{
        padding: `${contentPadding}px`,
        paddingTop: `calc(${headerHeight}px + ${contentPadding}px)`,
        minHeight: "100vh",
        background: COLORS?.background ?? "#ffffff",
        fontFamily: "Poppins, sans-serif",
        color: COLORS?.darkText ?? "#111827",
        boxSizing: "border-box",
        display: "flex",
        justifyContent: "center",
      }}
    >
      <style>{`
        .inputs-row {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: ${gap}px;
          align-items: start;
          width: 100%;
          max-width: ${maxRowWidth}px;
        }

        .field-col {
          display: flex;
          flex-direction: column;
          align-items: center; /* center label+input inside each column */
          gap: ${Math.round(10 * scale)}px;
        }

        .lbl {
          color: #4986D0;
          font-weight: 600;
          font-size: ${labelSize}px;
          line-height: ${labelLineHeight}px;
          align-self: flex-start; /* label left-aligned within its column to match screenshot */
          margin-left: 4px;
        }

        .input-wrap {
          width: 100%;
          display: flex;
          justify-content: flex-start; /* keep input starting from left within column */
        }

        .buttons-row {
          display: flex;
          justify-content: flex-end;
          gap: ${buttonsGap}px;
          margin-top: ${buttonsTop}px;
          width: 100%;
          max-width: ${maxRowWidth}px;
        }

        .btn-outline {
          padding: ${Math.round(8 * scale)}px ${Math.round(18 * scale)}px;
          height: ${Math.round(40 * scale)}px;
          background: #fff;
          color: ${COLORS?.primary ?? "#056BB6"};
          border: 1px solid ${COLORS?.primary ?? "#056BB6"};
          border-radius: ${Math.round(22 * scale)}px;
          font-weight: 500;
          cursor: pointer;
          font-family: Poppins, sans-serif;
        }

        .btn-primary {
          padding: ${Math.round(8 * scale)}px ${Math.round(18 * scale)}px;
          height: ${Math.round(40 * scale)}px;
          background: ${COLORS?.primary ?? "#056BB6"};
          color: #fff;
          border-radius: ${Math.round(22 * scale)}px;
          border: none;
          font-weight: 500;
          cursor: pointer;
          font-family: Poppins, sans-serif;
        }

        /* responsive breakpoints using scaled thresholds */
        @media (max-width: ${Math.round(1100 * scale)}px) {
          .inputs-row { grid-template-columns: repeat(2, 1fr); gap: ${Math.round(
            20 * scale
          )}px; }
        }
        @media (max-width: ${Math.round(680 * scale)}px) {
          .inputs-row { grid-template-columns: 1fr; }
          .buttons-row { justify-content: flex-start; }
          .lbl { align-self: flex-start; }
        }
      `}</style>

      {/* main container that holds inputs + buttons (no extra card per your request) */}
      <div style={{ width: "100%", maxWidth: `${maxRowWidth}px` }}>
        {/* Inputs row: 4 columns (each is label + input vertically centered in the column) */}
        <div className="inputs-row" role="group" aria-label="Finance inputs">
          {/* 1 - User */}
          <div className="field-col">
            <div className="lbl">User</div>
            <div
              className="input-wrap"
              style={{ width: "100%", maxWidth: `${inputWidth}px` }}
            >
              <BaseInput
                name="user"
                label={null}
                placeholder="Add user"
                value={record.user}
                onChange={handleChange("user")}
                variant="outlined"
                className=""
                // forward style for input height via style prop
                style={{ height: `${inputHeight}px` }}
              />
            </div>
          </div>

          {/* 2 - Company */}
          <div className="field-col">
            <div className="lbl">Company</div>
            <div
              className="input-wrap"
              style={{ width: "100%", maxWidth: `${inputWidth}px` }}
            >
              <Select
                name="company"
                value={record.company}
                onChange={handleChange("company")}
                options={COMPANIES}
                placeholder="Add company"
                variant="outlined"
                searchable
                className=""
                // If your Select supports a style prop, this passes width/height
                style={{ height: `${inputHeight}px`, width: "100%" }}
              />
            </div>
          </div>

          {/* 3 - Start date */}
          <div className="field-col">
            <div className="lbl">Start date</div>
            <div
              className="input-wrap"
              style={{ width: "100%", maxWidth: `${inputWidth}px` }}
            >
              <DateInput
                name="startDate"
                placeholder="Add start date"
                value={record.startDate}
                onChange={handleChange("startDate")}
                variant="calendar"
                showCalendarIcon={true}
                className=""
                style={{ height: `${inputHeight}px`, width: "100%" }}
              />
            </div>
          </div>

          {/* 4 - End date */}
          <div className="field-col">
            <div className="lbl">End date</div>
            <div
              className="input-wrap"
              style={{ width: "100%", maxWidth: `${inputWidth}px` }}
            >
              <DateInput
                name="endDate"
                placeholder="Add end date"
                value={record.endDate}
                onChange={handleChange("endDate")}
                variant="calendar"
                showCalendarIcon={true}
                className=""
                style={{ height: `${inputHeight}px`, width: "100%" }}
              />
            </div>
          </div>
        </div>

        {/* buttons under inputs, right-aligned and side-by-side */}
        <div className="buttons-row" aria-hidden="true">
          <button className="btn-outline" type="button" onClick={handleAdd}>
            Add
          </button>
          <button className="btn-primary" type="button" onClick={handleSave}>
            Save
          </button>
        </div>
      </div>
    </main>
  );
}
