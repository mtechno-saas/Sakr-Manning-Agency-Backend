import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { ASSETS } from "../../utils/constants";
import Button from "../common/Button";
import { useReferenceData } from "../../hooks/useReferenceData";
import { useQuickApply } from "../../hooks/dashboard/useQuickApply";
import { useApplicationStatus } from "../../hooks/useApplicationStatus";
import { jobOrdersApi } from "../../services/Dashboard/jobOrdersApi";
import { Paperclip } from 'lucide-react';

// Styles matching the modern aesthetic
const styles = {
    container: {
        minHeight: "100vh",
        display: "flex",
        flexDirection: "row",
        alignItems: "center",
        justifyContent: "flex-end",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        padding: "20px 60px",
        fontFamily: "'Poppins', sans-serif",
        position: "relative",
    },
    leftContent: {
        position: "absolute",
        left: "20px", // Align with container padding
        top: "30%",
        transform: "translateY(-50%)",
        zIndex: 2,
        width: "calc(55% - 60px)", // 2/3 of container width minus padding
        maxWidth: "none",
        color: "#ffffff",
        paddingLeft: "20px", // Start from 1/3 mark (middle of first third)
    },
    leftTitle: {
        fontSize: "32px",
        fontWeight: "500",
        lineHeight: "1.8",
        textShadow: "2px 2px 4px rgba(0,0,0,0.3)",
        margin: 0,
    },
    overlay: {
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "linear-gradient(to right, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.1) 100%)",
        zIndex: 1,
    },
    card: {
        background: "#ffffff",
        borderRadius: "20px",
        boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
        padding: "20px",
        width: "100%",
        maxWidth: "500px",
        // marginRight: "60px",
        marginRight: 0,
        position: "relative",
        overflow: "hidden",
        zIndex: 2,
    },
    title: {
        fontSize: "24px",
        fontWeight: "600",
        color: "#0065AF",
        marginBottom: "2px",
        textAlign: "start",
    },
    subtitle: {
        fontSize: "14px",
        color: "#64748b",
        marginBottom: "12px",
        textAlign: "start",
    },
    inputGroup: {
        marginBottom: "2px",
    },
    label: {
        display: "block",
        fontSize: "14px",
        fontWeight: "500",
        color: "#475569",
        marginBottom: "8px",
    },
    input: {
        width: "100%",
        padding: "12px 16px",
        borderRadius: "10px",
        border: "1px solid #cbd5e1",
        fontSize: "15px",
        color: "#1e293b",
        transition: "all 0.2s",
        outline: "none",
        boxSizing: "border-box",
    },
    fileInput: {
        border: "2px dashed #cbd5e1",
        padding: "10px",
        textAlign: "center",
        cursor: "pointer",
        borderRadius: "10px",
        background: "#f8fafc",
        transition: "all 0.2s",
        position: "relative",
    },
    fileInputIcon: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        fontSize: "32px",
        marginBottom: "2px",
        color: "#64748b",
    },
    error: {
        color: "#ef4444",
        fontSize: "12px",
        marginTop: "4px",
    },
    successCard: {
        textAlign: "center",
        padding: "40px 20px",
    },
};

const QuickApply = () => {
    const navigate = useNavigate();
    const [vacancies, setVacancies] = React.useState([]);
    const [loadingVacancies, setLoadingVacancies] = React.useState(false);

    // Custom hook for quick apply
    const {
        submitApplication,
        isSubmitting,
        isSubmitted,
        error: submitError,
        clearError
    } = useQuickApply();

    // Check application status to auto-redirect pending/active users to the form
    const { status, isLoading: statusLoading } = useApplicationStatus();

    useEffect(() => {
        if (!statusLoading && (status === "Pending" || status === "Active")) {
            navigate("/form", { replace: true });
        }
    }, [status, statusLoading, navigate]);

    useEffect(() => {
        const fetchVacancies = async () => {
            setLoadingVacancies(true);
            try {
                // Fetch all job positions (vacancies)
                const response = await jobOrdersApi.getJobPositions({ status: "Open" });
                // Handle both raw array and paginated response
                const list = Array.isArray(response) ? response : (response.results || response.job_positions || []);
                setVacancies(list);
            } catch (error) {
                console.error("Failed to fetch vacancies:", error);
            } finally {
                setLoadingVacancies(false);
            }
        };
        fetchVacancies();
    }, []);
    // React Hook Form
    const {
        register,
        handleSubmit,
        formState: { errors },
        watch,
    } = useForm();

    // Watch file input to show selected filename
    const cvFile = watch("file");

    // Fetch positions from backend
    const { positions, loadSpecificType } = useReferenceData({ loadOnMount: false });

    useEffect(() => {
        loadSpecificType("positions");
    }, [loadSpecificType]);

    // Handle form submission
    const onSubmit = async (data) => {
        // Find selected vacancy for details
        let job_position_details = null;
        if (data.job_position) {
            const selectedVacancy = vacancies.find(v => v.id === parseInt(data.job_position));
            if (selectedVacancy) {
                job_position_details = selectedVacancy;
            }
        }

        const result = await submitApplication({
            ...data,
            job_position_details
        }, positions);

        if (result.success) {
            // Redirect after showing success message
            setTimeout(() => {
                navigate("/");
            }, 4000);
        }
    };

    // Success Screen
    if (isSubmitted) {
        return (
            <div style={styles.container}>

                <div style={styles.overlay}></div>
                <div style={styles.leftContent}>
                    <h1 style={styles.leftTitle}>
                        Create detailed crew profiles with a few simple steps.
                    </h1>
                </div>
                <div style={styles.card}>
                    <div style={styles.successCard}>
                        <div style={{ fontSize: "48px", marginBottom: "20px" }}>🎉</div>
                        <h2 style={styles.title}>Application Received!</h2>
                        <p style={{ ...styles.subtitle, fontSize: "16px" }}>
                            Your application is now <strong>Pending Review</strong>.
                            <br />
                            <br />
                            Our recruiters will review your CV and contact you shortly with next steps.
                        </p>
                        <p style={{ fontSize: "12px", color: "#94a3b8", marginTop: "16px" }}>
                            Redirecting to Home page...
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    // Application Form
    return (
        <>
            <div className="bg-white shadow-sm z-40 px-16 py-3 flex items-center gap-4">
                <img src={ASSETS.LOGO} alt="Sakr Logo" className="w-10 h-10 object-contain" />
                <h1 className="text-lg font-medium text-gray-900">SAKR MANNING AGENCY</h1>
            </div>

            <div style={{ ...styles.container, backgroundImage: `url(${ASSETS.QUICKBG})` }}>
                <div style={styles.overlay}></div>
                <div style={styles.leftContent}>
                    <h1 style={styles.leftTitle}>
                        Create detailed crew profiles with a few simple steps.
                    </h1>
                </div>
                <div style={styles.card}>
                    {/* <div style={{ textAlign: "center", marginBottom: "20px" }}>
                    <img src={ASSETS.LOGO} alt="Sakr Maritime" height="40" />
                </div> */}

                    <h1 style={styles.title}>Quick Apply</h1>
                    <p style={styles.subtitle}>Enter your details to start with Sakr Mining Agency</p>

                    {/* Error Message */}
                    {submitError && (
                        <div style={{
                            padding: '12px',
                            background: '#fef2f2',
                            color: '#dc2626',
                            borderRadius: '8px',
                            marginBottom: '20px',
                            fontSize: '14px',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center'
                        }}>
                            <span>{submitError}</span>
                            <button
                                onClick={clearError}
                                style={{
                                    background: 'none',
                                    border: 'none',
                                    color: '#dc2626',
                                    cursor: 'pointer',
                                    fontSize: '18px',
                                    padding: '0 4px'
                                }}
                            >
                                ×
                            </button>
                        </div>
                    )}

                    <form onSubmit={handleSubmit(onSubmit)}>
                        {/* Full Name */}
                        <div style={styles.inputGroup}>
                            <label style={styles.label}>Full Name *</label>
                            <input
                                style={styles.input}
                                placeholder="Enter your name"
                                {...register("full_name", {
                                    required: "Name is required",
                                    minLength: {
                                        value: 2,
                                        message: "Name must be at least 2 characters"
                                    }
                                })}
                            />
                            {errors.full_name && (
                                <p style={styles.error}>{errors.full_name.message}</p>
                            )}
                        </div>

                        {/* Email */}
                        <div style={styles.inputGroup}>
                            <label style={styles.label}>Email Address *</label>
                            <input
                                type="email"
                                style={styles.input}
                                placeholder="Enter your email"
                                {...register("email", {
                                    required: "Email is required",
                                    pattern: {
                                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                                        message: "Invalid email address"
                                    }
                                })}
                            />
                            {errors.email && (
                                <p style={styles.error}>{errors.email.message}</p>
                            )}
                        </div>

                        {/* Phone Number */}
                        <div style={styles.inputGroup}>
                            <label style={styles.label}>Phone Number *</label>
                            <input
                                style={styles.input}
                                placeholder="+201242222222"
                                {...register("phone_number", {
                                    required: "Phone number is required",
                                    minLength: {
                                        value: 8,
                                        message: "Phone number must be at least 8 digits"
                                    }
                                })}
                            />
                            {errors.phone_number && (
                                <p style={styles.error}>{errors.phone_number.message}</p>
                            )}
                        </div>

                        {/* Position */}
                        <div style={styles.inputGroup}>
                            <label style={styles.label}>General Position (Rank)</label>
                            <select
                                style={styles.input}
                                {...register("position")}
                            >
                                <option value="">Select Rank (Optional)</option>
                                {(positions || []).map((pos) => (
                                    <option key={pos.id ?? pos.name} value={pos.id ?? pos.name}>
                                        {pos.name ?? pos.label ?? pos.title}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Available Vacancy */}
                        <div style={styles.inputGroup}>
                            <label style={styles.label}>Apply for Specific Vacancy</label>
                            <select
                                style={styles.input}
                                {...register("job_position")}
                                disabled={loadingVacancies}
                            >
                                <option value="">Select Vacancy (Optional)</option>
                                {vacancies.map((vacancy) => (
                                    <option key={vacancy.id} value={vacancy.id}>
                                        {vacancy.rank_name} {vacancy.ship_name ? `@ ${vacancy.ship_name}` : ""} {vacancy.company_name ? `(${vacancy.company_name})` : ""}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* CV Upload */}
                        <div style={styles.inputGroup}>
                            <label style={styles.label}>Upload CV *</label>
                            <div style={styles.fileInput}>
                                <div style={styles.fileInputIcon}><Paperclip size="16px" /></div>
                                <p style={{ fontSize: "14px", color: "#64748b", marginBottom: "8px" }}>
                                    <span style={{ fontSize: "14px", color: "#0065AF", marginRight: "4px" }}><u>Click</u></span>
                                    to upload or drag and drop
                                </p>
                                <input
                                    type="file"
                                    accept=".pdf,.doc,.docx"
                                    style={{
                                        position: "absolute",
                                        top: 0,
                                        left: 0,
                                        width: "100%",
                                        height: "100%",
                                        opacity: 0,
                                        cursor: "pointer"
                                    }}
                                    {...register("file", {
                                        required: "CV file is required",
                                        validate: {
                                            fileSize: (files) => {
                                                if (!files || !files[0]) return true;
                                                // Max 5MB
                                                return files[0].size <= 5242880 || "File size must be less than 5MB";
                                            },
                                            fileType: (files) => {
                                                if (!files || !files[0]) return true;
                                                const allowedTypes = [
                                                    'application/pdf',
                                                    'application/msword',
                                                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                                                ];
                                                return allowedTypes.includes(files[0].type) ||
                                                    "Only PDF and Word documents are allowed";
                                            }
                                        }
                                    })}
                                />
                            </div>
                            {cvFile && cvFile[0] && (
                                <p style={{ fontSize: "12px", color: "#64748b", marginTop: "8px" }}>
                                    📄 Selected: {cvFile[0].name} ({(cvFile[0].size / 1024).toFixed(2)} KB)
                                </p>
                            )}
                            {errors.file && <p style={styles.error}>{errors.file.message}</p>}
                        </div>

                        {/* Submit Button */}
                        <div style={{ marginTop: "8px" }}>
                            <Button
                                variant="primary"
                                type="submit"
                                disabled={isSubmitting}
                                style={{
                                    width: "100%",
                                    borderRadius: "24px",
                                    height: "48px",
                                    opacity: isSubmitting ? 0.7 : 1,
                                    cursor: isSubmitting ? 'not-allowed' : 'pointer'
                                }}
                            >
                                {isSubmitting ? "Submitting..." : "Submit Application"}
                            </Button>
                        </div>

                        <div style={{ textAlign: 'center', marginTop: '8px' }}>
                            <Button
                                variant="outlined"
                                type="button"
                                onClick={() => navigate('/')}
                                disabled={isSubmitting}
                                style={{
                                    width: "100%",
                                    borderRadius: "24px",
                                    height: "48px",
                                    cursor: isSubmitting ? 'not-allowed' : 'pointer',
                                    fontSize: '14px',
                                    opacity: isSubmitting ? 0.5 : 1
                                }}
                            >
                                Cancel
                            </Button>
                        </div>
                    </form>
                </div>
            </div>
        </>
    );
};

export default QuickApply;