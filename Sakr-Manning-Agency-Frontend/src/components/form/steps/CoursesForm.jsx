// components/forms/sections/CoursesForm.jsx
import React, { useState } from "react";
import { useFormContext, useFieldArray } from "react-hook-form";
import { Plus } from "lucide-react";
import { CourseModal } from "../modals/CourseModal";
import { CrudTable } from "../layout/FormTable";
import { StepSaveButton } from "../layout/StepSaveButton";

/**
 * CoursesForm Component - Refactored
 * 
 * Features:
 * - Modal-based add/edit
 * - Clean table display
 * - Better UX with proper feedback
 */
export function CoursesForm() {
  const { control, getValues } = useFormContext();
  const { fields, append, update, remove } = useFieldArray({
    control,
    name: "courses",
  });

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCourse, setEditingCourse] = useState(null);
  const [editingIndex, setEditingIndex] = useState(null);

  // Generate unique ID for new courses
  const generateId = () => `course-${Date.now()}-${Math.floor(Math.random() * 1000)}`;

  /**
   * Handle opening modal for adding new course
   */
  const handleAdd = () => {
    setEditingCourse(null);
    setIsModalOpen(true);
  };

  /**
   * Handle opening modal for editing existing course
   */
  const handleEdit = (course) => {
    const index = fields.findIndex((f) => f.id === course.id);
    setEditingIndex(index);
    const realData = getValues(`courses.${index}`);
    setEditingCourse({ ...course, _originalId: realData?.id || course.id });
    setIsModalOpen(true);
  };

  /**
   * Handle saving course (both add and edit)
   */
  const handleSave = (courseData) => {
    if (editingIndex !== null) {
      // Editing existing course
      update(editingIndex, {
        ...courseData,
        id: editingCourse._originalId,
      });
    } else {
      // Adding new course
      append({
        ...courseData,
        id: generateId(),
      });
    }
  };

  /**
   * Handle deleting course with confirmation
   */
  const handleDelete = (id) => {
    if (!window.confirm("Are you sure you want to delete this course?")) {
      return;
    }

    const index = fields.findIndex((f) => f.id === id);
    if (index !== -1) {
      remove(index);
    }
  };

  /**
   * Handle closing modal
   */
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingCourse(null);
    setEditingIndex(null);
  };

  // Table columns configuration - matching backend field names
  const columns = [
    { key: "course_name", label: "Course" },
    { key: "course_number", label: "Number" },
    { key: "issue_date", label: "Issue Date" },
    { key: "expiry_date", label: "Expiry Date" },
    { key: "issued_by", label: "Issued By" },
    { key: "issued_at", label: "Issued At" },
    { key: "country_of_issue", label: "Country" },
  ];

  return (
    <div className="w-full space-y-6">
      <StepSaveButton />
      {/* Header Section with Add Button */}
      <div className="bg-[#E8F4FD] rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Marine Courses
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Add your marine course certifications
            </p>
          </div>
          <button
            type="button"
            onClick={handleAdd}
            className="flex items-center gap-2 px-5 py-2.5 bg-[#CFDBEC] text-gray-800 rounded-lg hover:bg-[#b8c9de] transition-colors font-medium shadow-sm"
          >
            <Plus className="w-5 h-5" />
            Add Course
          </button>
        </div>
      </div>

      {/* Courses Table */}
      {fields.length > 0 && (
        <CrudTable
          data={fields}
          columns={columns}
          onEdit={handleEdit}
          onDelete={handleDelete}
          emptyMessage="No courses added yet. Click 'Add Course' to get started."
        />
      )}

      {/* Course Modal */}
      <CourseModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSave={handleSave}
        initialData={editingCourse}
      />
    </div>
  );
}