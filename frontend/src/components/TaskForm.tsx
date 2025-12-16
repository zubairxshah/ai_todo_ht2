"use client";

import { useState } from "react";
import type { TaskCreate, Tag } from "@/types";
import { PRIORITY_LABELS } from "@/types";

interface TaskFormProps {
  onSubmit: (task: TaskCreate) => Promise<void>;
  tags?: Tag[];
}

export default function TaskForm({ onSubmit, tags = [] }: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [priority, setPriority] = useState<number | "">("");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setLoading(true);
    try {
      const taskData: TaskCreate = {
        title: title.trim(),
      };

      if (dueDate) {
        taskData.due_date = new Date(dueDate).toISOString();
      }
      if (priority !== "") {
        taskData.priority = priority;
      }
      if (selectedTags.length > 0) {
        taskData.tag_ids = selectedTags;
      }

      await onSubmit(taskData);

      // Reset form
      setTitle("");
      setDueDate("");
      setPriority("");
      setSelectedTags([]);
      setShowAdvanced(false);
    } finally {
      setLoading(false);
    }
  };

  const toggleTag = (tagId: string) => {
    setSelectedTags((prev) =>
      prev.includes(tagId)
        ? prev.filter((id) => id !== tagId)
        : [...prev, tagId]
    );
  };

  return (
    <form onSubmit={handleSubmit} className="mb-6">
      {/* Main Input Row */}
      <div className="flex gap-2">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What needs to be done?"
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={loading}
        />
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className={`px-3 py-2 border rounded-lg transition-colors ${
            showAdvanced
              ? "bg-blue-50 border-blue-300 text-blue-600"
              : "border-gray-300 text-gray-500 hover:border-blue-300 hover:text-blue-600"
          }`}
          title="Advanced options"
        >
          <svg
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
            />
          </svg>
        </button>
        <button
          type="submit"
          disabled={loading || !title.trim()}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Adding..." : "Add"}
        </button>
      </div>

      {/* Advanced Options */}
      {showAdvanced && (
        <div className="mt-3 p-4 bg-gray-50 rounded-lg border border-gray-200 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Due Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Due Date
              </label>
              <input
                type="datetime-local"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Priority */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority
              </label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value ? parseInt(e.target.value) : "")}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">None</option>
                {Object.entries(PRIORITY_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Tags */}
          {tags.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tags
              </label>
              <div className="flex flex-wrap gap-2">
                {tags.map((tag) => (
                  <button
                    key={tag.id}
                    type="button"
                    onClick={() => toggleTag(tag.id)}
                    className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                      selectedTags.includes(tag.id)
                        ? "border-transparent text-white"
                        : "border-gray-300 text-gray-600 hover:border-gray-400"
                    }`}
                    style={{
                      backgroundColor: selectedTags.includes(tag.id) ? tag.color : "transparent",
                    }}
                  >
                    {tag.name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </form>
  );
}
