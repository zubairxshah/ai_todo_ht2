"use client";

import { useState, useEffect } from "react";
import type { TaskFilterParams, TagWithCount } from "@/types";
import { PRIORITY_LABELS } from "@/types";

interface FilterBarProps {
  filters: TaskFilterParams;
  onFiltersChange: (filters: TaskFilterParams) => void;
  tags: TagWithCount[];
}

export default function FilterBar({ filters, onFiltersChange, tags }: FilterBarProps) {
  const [searchInput, setSearchInput] = useState(filters.search || "");

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchInput !== filters.search) {
        onFiltersChange({ ...filters, search: searchInput || undefined });
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchInput]);

  const handleStatusChange = (status: TaskFilterParams["status"]) => {
    onFiltersChange({ ...filters, status });
  };

  const handlePriorityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    onFiltersChange({
      ...filters,
      priority: value ? parseInt(value) : undefined,
    });
  };

  const handleTagChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFiltersChange({
      ...filters,
      tag_id: e.target.value || undefined,
    });
  };

  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const [sort_by, sort_order] = e.target.value.split("-") as [TaskFilterParams["sort_by"], TaskFilterParams["sort_order"]];
    onFiltersChange({ ...filters, sort_by, sort_order });
  };

  const handleOverdueToggle = () => {
    onFiltersChange({ ...filters, overdue: !filters.overdue });
  };

  const clearFilters = () => {
    setSearchInput("");
    onFiltersChange({});
  };

  const hasActiveFilters = filters.search || filters.priority || filters.tag_id || filters.overdue || filters.status !== "all";

  return (
    <div className="mb-6 space-y-3">
      {/* Search Bar */}
      <div className="relative">
        <input
          type="text"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          placeholder="Search tasks..."
          className="w-full px-4 py-2 pl-10 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm"
        />
        <svg
          className="absolute left-3 top-2.5 h-5 w-5 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      </div>

      {/* Filter Controls */}
      <div className="flex flex-wrap gap-2 items-center">
        {/* Status Tabs */}
        <div className="flex bg-gray-100 rounded-lg p-1">
          {(["all", "pending", "completed"] as const).map((status) => (
            <button
              key={status}
              onClick={() => handleStatusChange(status)}
              className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                (filters.status || "all") === status
                  ? "bg-white text-blue-600 shadow-sm"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>

        {/* Priority Filter */}
        <select
          value={filters.priority || ""}
          onChange={handlePriorityChange}
          className="px-3 py-1.5 text-sm bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Priorities</option>
          {Object.entries(PRIORITY_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>

        {/* Tag Filter */}
        {tags.length > 0 && (
          <select
            value={filters.tag_id || ""}
            onChange={handleTagChange}
            className="px-3 py-1.5 text-sm bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Tags</option>
            {tags.map((tag) => (
              <option key={tag.id} value={tag.id}>
                {tag.name} ({tag.task_count})
              </option>
            ))}
          </select>
        )}

        {/* Overdue Toggle */}
        <button
          onClick={handleOverdueToggle}
          className={`px-3 py-1.5 text-sm rounded-lg border transition-colors ${
            filters.overdue
              ? "bg-red-50 border-red-200 text-red-700"
              : "bg-white border-gray-200 text-gray-600 hover:border-red-200 hover:text-red-600"
          }`}
        >
          Overdue
        </button>

        {/* Sort */}
        <select
          value={`${filters.sort_by || "created_at"}-${filters.sort_order || "desc"}`}
          onChange={handleSortChange}
          className="px-3 py-1.5 text-sm bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="created_at-desc">Newest First</option>
          <option value="created_at-asc">Oldest First</option>
          <option value="due_date-asc">Due Date (Soonest)</option>
          <option value="due_date-desc">Due Date (Latest)</option>
          <option value="priority-asc">Priority (High to Low)</option>
          <option value="priority-desc">Priority (Low to High)</option>
          <option value="title-asc">Title (A-Z)</option>
          <option value="title-desc">Title (Z-A)</option>
        </select>

        {/* Clear Filters */}
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 underline"
          >
            Clear filters
          </button>
        )}
      </div>
    </div>
  );
}
