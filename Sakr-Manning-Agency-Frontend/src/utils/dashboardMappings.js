// FIX: Field name alignment between frontend & backend
export const FIELD_MAPPINGS = {
  interviews: {
    candidate: "user", // backend uses 'user', frontend uses 'candidate'
    scheduled_date: "date",
    scheduled_time: "time",
    interview_type: "type",
  },
  finance: {
    userId: "user",
    companyId: "company",
    startDate: "start_date",
    endDate: "end_date",
  },
  documents: {
    name: "user.name", // Nested field path
    position: "position.name",
  },
};
