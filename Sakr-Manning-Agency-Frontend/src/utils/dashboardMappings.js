export const FIELD_MAPPINGS = {
  interviews: {
    candidate: "user",
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
