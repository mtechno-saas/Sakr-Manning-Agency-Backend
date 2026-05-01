import React, { useRef, useState, useEffect } from "react";
import { LogOut, Pencil } from "lucide-react";

/**
 * Sidebar - Left navigation panel with user profile and step navigation
 * 
 * Props:
 *  - steps: array of step objects with { label, icon }
 *  - currentStep: active step index
 *  - goToStep: function to navigate to step
 *  - userProfile: object with { photo, name, position, lastUpdate, availableDate, registerId, mobile }
 *  - onLogout: logout handler
 *  - onImageChange: callback for when profile image is changed
 */

export function Sidebar({
    steps,
    currentStep,
    goToStep,
    userProfile,
    onLogout,
    onImageChange
}) {
    const fileInputRef = useRef(null);
    const [previewUrl, setPreviewUrl] = useState(null);

    // Sync previewUrl with userProfile.photo when it changes
    useEffect(() => {
        if (userProfile?.photo) {
            if (typeof userProfile.photo === 'string') {
                setPreviewUrl(userProfile.photo);
            } else if (userProfile.photo instanceof File) {
                const objectUrl = URL.createObjectURL(userProfile.photo);
                setPreviewUrl(objectUrl);
                return () => URL.revokeObjectURL(objectUrl);
            }
        }
    }, [userProfile?.photo]);

    const handleImageClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = (e) => {
        const file = e.target.files?.[0];
        if (file) {
            // Validate file type
            if (!file.type.startsWith("image/")) {
                alert("Please select an image file");
                return;
            }
            // Validate file size (5MB max)
            if (file.size > 5 * 1024 * 1024) {
                alert("Image size must be less than 5MB");
                return;
            }

            // Notify parent component
            onImageChange?.(file);
        }
    };
    return (
        <div className="w-72 bg-white border-r border-gray-200 flex flex-col h-full sticky top-0 rounded-lg">
            {/* User Profile Card */}
            <div className="p-4 border-b border-gray-200">
                <div className="flex flex-col items-center text-center">
                    {/* Profile Photo with Upload */}
                    <div
                        className="w-16 h-16 rounded-full overflow-hidden bg-gray-200 mb-3 relative group cursor-pointer"
                        onClick={handleImageClick}
                        title="Click to upload profile photo"
                    >
                        <input
                            name="profile_photo"
                            ref={fileInputRef}
                            type="file"
                            accept="image/*"
                            className="hidden"
                            onChange={handleFileChange}
                        />

                        {previewUrl ? (
                            <img
                                src={previewUrl}
                                alt={userProfile?.name || "Profile"}
                                className="w-full h-full object-cover"
                            />
                        ) : (
                            <div className="w-full h-full flex items-center justify-center bg-gray-300 text-gray-600 text-2xl font-semibold">
                                {userProfile?.name?.[0]?.toUpperCase() || "U"}
                            </div>
                        )}

                        {/* Pen Icon Overlay */}
                        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all duration-200 flex items-center justify-center rounded-full">
                            <Pencil className="w-5 h-5 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                        </div>
                    </div>

                    <div className="flex flex-col w-full items-start justify-start min-w-0 overflow-hidden">
                        {/* User Info */}
                        <h3 className="font-semibold text-sm text-[#064573] mb-1">
                            {userProfile?.name || "Demo User"}
                        </h3>
                        <p className="font-semibold text-sm text-[#064573] mb-1">
                            {userProfile?.position || "Demo Position"}
                        </p>

                        {/* Date of Availability */}
                        {userProfile?.availableDate && (
                            <div className="flex justify-between gap-2">
                                <span className="font-semibold text-sm text-[#064573] mb-1 shrink-0">Available:</span>
                                <span className="font-medium text-sm">
                                    {(() => {
                                        const parts = userProfile.availableDate.split("-");
                                        if (parts.length === 3) return `${parts[2]}-${parts[1]}-${parts[0]}`;
                                        return userProfile.availableDate;
                                    })()}
                                </span>
                            </div>
                        )}

                        {/* Availability and Salary*/}
                        <div className="flex justify-between gap-2">
                            <span className="font-semibold text-sm text-[#064573] mb-1 shrink-0">Salary:</span>
                            <span className="font-medium">{userProfile?.expectedSalary + " " + userProfile?.expectedSalaryCurrency || "Demo Salary"}</span>
                        </div>
                        {/* Contact */}
                        <div className="flex justify-between gap-2">
                            <span className="font-semibold text-sm text-[#064573] mb-1 shrink-0">Mobile:</span>
                            <span className="font-medium">{userProfile?.mobile || "Demo Mobile"}</span>
                        </div>
                        <div className="flex justify-between gap-2 min-w-0">
                            <span className="font-semibold text-sm text-[#064573] mb-1 shrink-0">Email:</span>
                            <span className="font-medium text-sm truncate min-w-0" title={userProfile?.email}>{userProfile?.email || "Demo Email"}</span>
                        </div>

                        {/* Register ID */}
                        {/* <div className="flex justify-between gap-2">
                            <span className="font-semibold text-sm text-[#064573] mb-1">Register code:</span>
                            <span className="font-medium">{userProfile?.registerId || "Demo Register ID"}</span>
                        </div> */}

                    </div>

                </div>
            </div>

            {/* Navigation Steps */}
            <nav className="flex-1 overflow-y-auto py-2 px-4">
                {steps.map((step, index) => {
                    const isActive = currentStep === index;
                    const isCompleted = currentStep > index;
                    const Icon = step.icon[index];

                    return (
                        <button
                            key={index}
                            onClick={() => goToStep(index)}
                            className={`
                w-full flex items-center gap-3 px-4 py-3 text-left transition-colors rounded-[16px]
                ${isActive
                                    ? "bg-[#0C64A4] text-white border-r-4 border-[#0C64A4]"
                                    : isCompleted
                                        ? "text-[#0C64A4]"
                                        : "text-[#0C64A4]"
                                }
              `}
                        >
                            {/* Icon */}
                            <div className="w-8 h-8 flex-shrink-0">
                                {/* <img
                                    src={step.icon[index]}
                                    alt=""
                                    className={`w-full h-full ${isActive ? "bg-white rounded-full" : ""} ${!isActive && !isCompleted ? "opacity-50" : ""}`}
                                /> */}
                                <Icon className={`w-full h-full ${isActive ? "text-white" : ""} ${!isActive && !isCompleted ? "opacity-50" : ""}`} />
                            </div>

                            {/* Label */}
                            <span className={`text-sm font-medium ${isActive ? "font-semibold" : ""}`}>
                                {step.label}
                            </span>
                        </button>
                    );
                })}
            </nav>

            {/* Logout Button */}
            <button
                onClick={onLogout}
                className="flex items-center gap-3 px-4 py-4 text-left text-red-600 hover:bg-red-50 transition-colors border-t border-gray-200"
            >
                <LogOut className="w-5 h-5" />
                <span className="text-sm font-medium">Log out</span>
            </button>
        </div>
    );
}