import { useState } from "react";
import { useForm, FormProvider } from "react-hook-form";

// Import the actual DocumentsForm component structure
import { DocumentsForm } from "./components/form/steps/DocumentsForm";

// Wrapper component for testing
export default function DocumentFormTest() {
    const methods = useForm({
        mode: "onChange",
        defaultValues: {
            documents: [],
        },
    });

    const [showData, setShowData] = useState(false);
    const documents = methods.watch("documents");

    const handleReset = () => {
        if (window.confirm("Reset all documents?")) {
            methods.reset({ documents: [] });
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 p-8">
            <div className="max-w-6xl mx-auto">
                {/* Test Header */}
                <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900 mb-2">
                                Document Form Test
                            </h1>
                            <p className="text-gray-600">
                                Testing DocumentsForm component with DocumentModal and CrudTable
                            </p>
                        </div>
                        <button
                            onClick={handleReset}
                            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                        >
                            Reset All
                        </button>
                    </div>
                </div>

                {/* Form Provider Wrapper */}
                <FormProvider {...methods}>
                    <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
                        <DocumentsForm />
                    </div>
                </FormProvider>

                {/* Debug Panel */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-gray-900">
                            Form Data (Debug)
                        </h3>
                        <button
                            onClick={() => setShowData(!showData)}
                            className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                        >
                            {showData ? "Hide" : "Show"} JSON Data
                        </button>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="bg-gray-50 rounded-lg p-4">
                            <div className="text-sm text-gray-500 mb-1">Total Documents</div>
                            <div className="text-2xl font-bold text-gray-900">{documents.length}</div>
                        </div>
                        <div className="bg-gray-50 rounded-lg p-4">
                            <div className="text-sm text-gray-500 mb-1">Form Valid</div>
                            <div className="text-2xl font-bold text-gray-900">
                                {methods.formState.isValid ? "✓" : "✗"}
                            </div>
                        </div>
                    </div>

                    {showData && (
                        <div className="bg-gray-50 rounded-lg p-4 overflow-auto">
                            <pre className="text-xs text-gray-800 whitespace-pre-wrap">
                                {JSON.stringify(documents, null, 2)}
                            </pre>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
