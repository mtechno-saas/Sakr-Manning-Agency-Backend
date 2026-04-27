import React, { useState } from "react";
import { CheckCircle2, XCircle, AlertCircle } from "lucide-react";

const ResponsiveAnalysis = () => {
  const [activeTab, setActiveTab] = useState("issues");

  const issues = [
    {
      page: "Contact Page",
      severity: "high",
      problems: [
        "Form inputs use fixed width (w-[592px]) - breaks on mobile",
        "Map image fixed at 600px width - not responsive",
        "No mobile-first approach for form layout",
        "Team cards use fixed gaps (lg:gap-[183px]) causing overflow",
      ],
      fixes: [
        "Replace all fixed widths with w-full and max-w-*",
        "Use aspect-ratio for map image responsiveness",
        "Implement mobile-first flex-col to flex-row pattern",
        "Use responsive gap utilities (gap-4 md:gap-8 lg:gap-12)",
      ],
    },
    {
      page: "Home Page",
      severity: "high",
      problems: [
        "Hero overlay content uses fixed margin (mt-[-30px])",
        "Service tags overflow on mobile (whitespace-nowrap with fixed gaps)",
        "CTA section fixed height (h-[235px]) cuts content on small screens",
        "Jobs section width (w-2/3) too wide on mobile",
      ],
      fixes: [
        "Use relative positioning instead of negative margins",
        "Make service tags scrollable or wrap on mobile",
        "Use min-h-* instead of fixed height, add py-* for spacing",
        "Use w-full px-4 on mobile, w-2/3 only on lg+ screens",
      ],
    },
    {
      page: "About Page",
      severity: "medium",
      problems: [
        "Values cards have inconsistent heights (min-h-[200px] lg:h-[220px])",
        "Large text (lg:text-[32px]) doesn't scale between breakpoints",
        "Image heights fixed (h-[480px] md:h-[596px])",
        "Excessive horizontal padding (px-24) on vision section",
      ],
      fixes: [
        "Use min-h-[200px] consistently, let content determine height",
        "Add more breakpoints: text-base sm:text-lg md:text-xl lg:text-2xl xl:text-3xl",
        "Use aspect-ratio utilities instead of fixed heights",
        "Use responsive padding: px-4 sm:px-6 md:px-12 lg:px-24",
      ],
    },
    {
      page: "Services Page",
      severity: "medium",
      problems: [
        "Hero image fixed dimensions (lg:w-[636px] lg:h-[596px])",
        "Service tags use fixed widths (w-full lg:w-[579px])",
        "Fixed gaps between tags (gap-[71px]) cause layout issues",
        "CTA section fixed height breaks on mobile",
      ],
      fixes: [
        "Use w-full lg:w-1/2 with aspect-square for responsive sizing",
        "Remove fixed widths, use w-full throughout",
        "Use responsive gap utilities (gap-4 md:gap-8 lg:gap-12)",
        "Use min-h-* and py-* for flexible CTA height",
      ],
    },
  ];

  const designDiscrepancies = [
    {
      element: "Header",
      figma: "No search icon visible",
      code: "Search icon present (commented out)",
      recommendation: "Remove or keep commented based on requirements",
    },
    {
      element: "Typography",
      figma: "Smooth scaling with consistent line heights",
      code: "Jumps between sizes, inconsistent leading",
      recommendation: "Use fluid typography with clamp() or more breakpoints",
    },
    {
      element: "Spacing",
      figma: "Consistent spacing system (8px, 16px, 24px, 32px)",
      code: "Mixed spacing (gap-[71px], gap-[183px], custom values)",
      recommendation:
        "Stick to Tailwind spacing scale (gap-4, gap-8, gap-12, gap-16)",
    },
    {
      element: "Containers",
      figma: "Consistent max-width around 1200-1400px",
      code: "Inconsistent: max-w-9xl, max-w-6xl, no max-width",
      recommendation: "Define standard: max-w-7xl (1280px) or max-w-screen-xl",
    },
    {
      element: "Cards",
      figma: "Equal height cards in grids",
      code: "Height varies with content",
      recommendation: "Add h-full to card children or use grid-auto-rows",
    },
  ];

  const responsivePattern = {
    before: `// ❌ Current Pattern
<div className="w-[600px] h-[520px]">
  <ImageBlock src={image} />
</div>

<Input 
  className="w-[592px] h-[70px]" 
/>

<div className="flex gap-[183px]">
  {/* content */}
</div>`,
    after: `// ✅ Responsive Pattern
<div className="w-full max-w-2xl aspect-video">
  <ImageBlock 
    src={image} 
    className="w-full h-full object-cover"
  />
</div>

<Input 
  className="w-full max-w-xl h-16 sm:h-18 md:h-20" 
/>

<div className="flex flex-col md:flex-row gap-8 md:gap-12 lg:gap-16">
  {/* content */}
</div>`,
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case "high":
        return "text-red-600 bg-red-50";
      case "medium":
        return "text-orange-600 bg-orange-50";
      case "low":
        return "text-yellow-600 bg-yellow-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 md:p-8">
            <h1 className="text-2xl md:text-3xl font-bold mb-2">
              Responsive Design Analysis
            </h1>
            <p className="text-blue-100">
              Sakr Manning Agency Landing Page - Issues & Fixes
            </p>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 bg-gray-50">
            <div className="flex overflow-x-auto">
              {["issues", "discrepancies", "pattern"].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-6 py-4 font-medium whitespace-nowrap transition-colors ${
                    activeTab === tab
                      ? "text-blue-600 border-b-2 border-blue-600 bg-white"
                      : "text-gray-600 hover:text-gray-900"
                  }`}
                >
                  {tab === "issues" && "🐛 Responsive Issues"}
                  {tab === "discrepancies" && "🎨 Design Discrepancies"}
                  {tab === "pattern" && "✨ Best Practices"}
                </button>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="p-6 md:p-8">
            {activeTab === "issues" && (
              <div className="space-y-8">
                {issues.map((issue, idx) => (
                  <div
                    key={idx}
                    className="border border-gray-200 rounded-xl overflow-hidden"
                  >
                    <div
                      className={`p-4 flex items-center gap-3 ${getSeverityColor(
                        issue.severity
                      )}`}
                    >
                      <AlertCircle className="w-5 h-5" />
                      <h3 className="font-bold text-lg">{issue.page}</h3>
                      <span className="ml-auto px-3 py-1 rounded-full text-xs font-semibold uppercase">
                        {issue.severity} Priority
                      </span>
                    </div>

                    <div className="p-6 space-y-6">
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <XCircle className="w-4 h-4 text-red-500" />
                          Problems Found
                        </h4>
                        <ul className="space-y-2">
                          {issue.problems.map((problem, pIdx) => (
                            <li
                              key={pIdx}
                              className="flex items-start gap-2 text-gray-700"
                            >
                              <span className="text-red-500 mt-1">•</span>
                              <span>{problem}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div>
                        <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-green-500" />
                          Recommended Fixes
                        </h4>
                        <ul className="space-y-2">
                          {issue.fixes.map((fix, fIdx) => (
                            <li
                              key={fIdx}
                              className="flex items-start gap-2 text-gray-700"
                            >
                              <span className="text-green-500 mt-1">✓</span>
                              <span>{fix}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === "discrepancies" && (
              <div className="space-y-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <p className="text-blue-800">
                    <strong>Note:</strong> These are differences between the
                    Figma design and current implementation.
                  </p>
                </div>

                {designDiscrepancies.map((item, idx) => (
                  <div
                    key={idx}
                    className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
                  >
                    <h3 className="font-bold text-lg text-gray-900 mb-4">
                      {item.element}
                    </h3>

                    <div className="grid md:grid-cols-2 gap-4 mb-4">
                      <div className="bg-purple-50 rounded-lg p-4">
                        <div className="text-xs font-semibold text-purple-600 mb-2">
                          FIGMA DESIGN
                        </div>
                        <p className="text-gray-700">{item.figma}</p>
                      </div>
                      <div className="bg-orange-50 rounded-lg p-4">
                        <div className="text-xs font-semibold text-orange-600 mb-2">
                          CURRENT CODE
                        </div>
                        <p className="text-gray-700">{item.code}</p>
                      </div>
                    </div>

                    <div className="bg-green-50 border-l-4 border-green-500 p-4">
                      <div className="text-xs font-semibold text-green-700 mb-1">
                        RECOMMENDATION
                      </div>
                      <p className="text-gray-700">{item.recommendation}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === "pattern" && (
              <div className="space-y-8">
                <div className="prose max-w-none">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">
                    Responsive Best Practices
                  </h2>
                  <p className="text-gray-700 mb-6">
                    Follow these patterns to ensure proper responsiveness across
                    all devices.
                  </p>
                </div>

                <div className="bg-gray-900 rounded-xl p-6 overflow-x-auto">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <div className="text-red-400 font-mono text-sm mb-4">
                        // ❌ BEFORE (Fixed Widths)
                      </div>
                      <pre className="text-gray-300 text-sm overflow-x-auto">
                        <code>{responsivePattern.before}</code>
                      </pre>
                    </div>
                    <div>
                      <div className="text-green-400 font-mono text-sm mb-4">
                        // ✅ AFTER (Responsive)
                      </div>
                      <pre className="text-gray-300 text-sm overflow-x-auto">
                        <code>{responsivePattern.after}</code>
                      </pre>
                    </div>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6 mt-8">
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6">
                    <h3 className="font-bold text-blue-900 mb-4 flex items-center gap-2">
                      <CheckCircle2 className="w-5 h-5" />
                      Mobile-First Approach
                    </h3>
                    <ul className="space-y-2 text-blue-800 text-sm">
                      <li>• Start with mobile styles</li>
                      <li>• Add sm:, md:, lg: progressively</li>
                      <li>• Use w-full as default</li>
                      <li>• Add max-w-* for large screens</li>
                    </ul>
                  </div>

                  <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6">
                    <h3 className="font-bold text-green-900 mb-4 flex items-center gap-2">
                      <CheckCircle2 className="w-5 h-5" />
                      Spacing System
                    </h3>
                    <ul className="space-y-2 text-green-800 text-sm">
                      <li>• Use Tailwind scale (4, 8, 12, 16)</li>
                      <li>• Avoid custom values like [183px]</li>
                      <li>• Use responsive gaps (gap-4 md:gap-8)</li>
                      <li>• Consistent padding across pages</li>
                    </ul>
                  </div>

                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6">
                    <h3 className="font-bold text-purple-900 mb-4 flex items-center gap-2">
                      <CheckCircle2 className="w-5 h-5" />
                      Typography Scaling
                    </h3>
                    <ul className="space-y-2 text-purple-800 text-sm">
                      <li>• Add more breakpoints</li>
                      <li>• Use consistent line-height</li>
                      <li>• Consider fluid typography</li>
                      <li>• Test readability on all sizes</li>
                    </ul>
                  </div>

                  <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-6">
                    <h3 className="font-bold text-orange-900 mb-4 flex items-center gap-2">
                      <CheckCircle2 className="w-5 h-5" />
                      Image Handling
                    </h3>
                    <ul className="space-y-2 text-orange-800 text-sm">
                      <li>• Use aspect-ratio utilities</li>
                      <li>• Add object-fit (cover/contain)</li>
                      <li>• Responsive image dimensions</li>
                      <li>• Consider next/image patterns</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer Note */}
        <div className="mt-6 bg-white rounded-xl p-6 shadow-md">
          <h3 className="font-bold text-gray-900 mb-3">
            📋 Files Needed for Complete Analysis:
          </h3>
          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
            {[
              "Section.jsx",
              "Card.jsx",
              "Button.jsx",
              "ImageBlock.jsx",
              "Input.jsx",
              "Newsletter.jsx",
              "InfiniteTicker.jsx",
              "globals.css",
              "constants.js",
            ].map((file) => (
              <div
                key={file}
                className="bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-sm font-mono text-gray-700"
              >
                {file}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResponsiveAnalysis;
