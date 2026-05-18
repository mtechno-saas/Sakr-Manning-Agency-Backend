import React from "react";
import { useNavigate } from "react-router-dom";
import { Clock, ArrowLeft, ShieldAlert, Award } from "lucide-react";
import { ASSETS } from "../../utils/constants";
import Button from "../common/Button";
import { useApplicationStatus } from "../../hooks/useApplicationStatus";
import LoadingScreen from "../dashboard/Components/Common/LoadingScreen";

const styles = {
    container: {
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        padding: "24px",
        fontFamily: "'Poppins', sans-serif",
        position: "relative",
    },
    overlay: {
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.8) 100%)",
        zIndex: 1,
    },
    card: {
        background: "rgba(255, 255, 255, 0.95)",
        backdropFilter: "blur(16px)",
        borderRadius: "24px",
        boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.5)",
        padding: "48px 40px",
        width: "100%",
        maxWidth: "540px",
        position: "relative",
        zIndex: 2,
        textAlign: "center",
        border: "1px solid rgba(255, 255, 255, 0.3)",
        transform: "translateY(0)",
        transition: "transform 0.3s ease, box-shadow 0.3s ease",
    },
    header: {
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        background: "rgba(255, 255, 255, 0.8)",
        backdropFilter: "blur(12px)",
        zIndex: 10,
        borderBottom: "1px solid rgba(226, 232, 240, 0.8)",
        boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.05)",
    },
    iconWrapper: {
        width: "88px",
        height: "88px",
        borderRadius: "50%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        margin: "0 auto 28px auto",
        boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.1)",
        position: "relative",
    },
    title: {
        fontSize: "26px",
        fontWeight: "700",
        color: "#0f172a",
        marginBottom: "16px",
        lineHeight: "1.3",
    },
    text: {
        fontSize: "15px",
        color: "#475569",
        lineHeight: "1.7",
        marginBottom: "32px",
    },
};

export const NotifyPage = () => {
    const navigate = useNavigate();
    const { status, isLoading } = useApplicationStatus();

    if (isLoading) {
        return (
            <LoadingScreen
                fullScreen={true}
                message="Checking Application State"
                subMessage="Directing you to the correct portal"
            />
        );
    }

    const renderContent = () => {
        switch (status) {
            case "Pending":
            default:
                return (
                    <>
                        <div style={{
                            ...styles.iconWrapper,
                            background: "linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)",
                            border: "1px solid #bfdbfe",
                        }}>
                            <Clock size={40} color="#0284c7" strokeWidth={1.8} />
                        </div>
                        <h1 style={styles.title}>Application Under Review</h1>
                        <p style={styles.text}>
                            Thank you for applying to <strong>Sakr Manning Agency</strong>.
                            Your Quick Apply submission has been received and is currently in our queue.
                            Our team of maritime recruiters is evaluating your profile.
                            <br />
                            <br />
                            Once approved, you will be authorized to access the full application forms
                            and proceed with the onboard onboarding pipeline.
                        </p>
                    </>
                );

            case "Blacklist":
                return (
                    <>
                        <div style={{
                            ...styles.iconWrapper,
                            background: "linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)",
                            border: "1px solid #fecaca",
                        }}>
                            <ShieldAlert size={40} color="#dc2626" strokeWidth={1.8} />
                        </div>
                        <h1 style={{ ...styles.title, color: "#991b1b" }}>Access Denied</h1>
                        <p style={styles.text}>
                            Your application cannot be processed at this time.
                            Please contact our support crew or primary administration for further
                            inquiries regarding your registration state.
                        </p>
                    </>
                );

            case "Active":
                return (
                    <>
                        <div style={{
                            ...styles.iconWrapper,
                            background: "linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)",
                            border: "1px solid #bbf7d0",
                        }}>
                            <Award size={40} color="#16a34a" strokeWidth={1.8} />
                        </div>
                        <h1 style={{ ...styles.title, color: "#166534" }}>Application Approved!</h1>
                        <p style={styles.text}>
                            Congratulations! Your initial quick apply has been approved by our crew managers.
                            You are now authorized to complete the comprehensive Seafarer profile.
                        </p>
                        <Button
                            variant="primary"
                            onClick={() => navigate("/form")}
                            style={{
                                width: "100%",
                                borderRadius: "24px",
                                height: "48px",
                                marginBottom: "16px",
                            }}
                        >
                            Proceed to Full Form
                        </Button>
                    </>
                );
        }
    };

    return (
        <>
            {/* Header branding */}
            <div className="bg-white shadow-sm z-40 px-6 md:px-16 py-4 flex items-center gap-4 fixed top-0 left-0 right-0" style={styles.header}>
                <img
                    src={ASSETS.LOGO}
                    alt="Sakr Logo"
                    className="w-10 h-10 object-contain rounded-full cursor-pointer"
                    onClick={() => navigate('/')}
                />
                <h1 className="text-base md:text-lg font-medium text-gray-900 tracking-wide cursor-pointer" onClick={() => navigate('/')}>
                    SAKR MANNING AGENCY
                </h1>
            </div>

            {/* Main content body */}
            <div style={{ ...styles.container, backgroundImage: `url(${ASSETS.QUICKBG})` }}>
                <div style={styles.overlay}></div>

                <div style={styles.card}>
                    {renderContent()}

                    <Button
                        variant="outlined"
                        onClick={() => navigate("/")}
                        style={{
                            width: "100%",
                            borderRadius: "24px",
                            height: "48px",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "8px",
                            fontSize: "15px",
                        }}
                    >
                        Back to Landing Page
                    </Button>
                </div>
            </div>
        </>
    );
};

export default NotifyPage;
