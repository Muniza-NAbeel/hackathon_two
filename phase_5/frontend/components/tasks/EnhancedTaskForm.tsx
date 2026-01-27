'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Modal } from '@/components/ui/Modal'
import type { Task, TaskCreate, TaskUpdate } from '@/types'

interface EnhancedTaskFormProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: TaskCreate | TaskUpdate) => Promise<void>
  task?: Task | null
  mode: 'create' | 'edit'
}

export function EnhancedTaskForm({
  isOpen,
  onClose,
  onSubmit,
  task,
  mode,
}: EnhancedTaskFormProps) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [dueDate, setDueDate] = useState('')
  const [reminderOption, setReminderOption] = useState('none') // none, 15min, 30min, 1hour, 1day, custom
  const [customReminder, setCustomReminder] = useState('')
  const [priority, setPriority] = useState('medium')
  const [status, setStatus] = useState('pending')
  const [recurrence, setRecurrence] = useState('none')
  const [tagInput, setTagInput] = useState('')
  const [tags, setTags] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<{
    title?: string
    description?: string
    general?: string
  }>({})

  // Priority auto-detection from title and description
  const detectPriorityFromText = (text: string): string => {
    const lowerText = text.toLowerCase()

    // Check for urgent keywords
    const urgentKeywords = ['urgent', 'asap', 'immediately', 'فوری', 'fori', 'zaruri']
    if (urgentKeywords.some(keyword => lowerText.includes(keyword))) {
      return 'urgent'
    }

    // Check for high priority keywords
    const highKeywords = ['high priority', 'high', 'important', 'ضروری', 'zaroori', 'important hai', 'zaruri hai']
    if (highKeywords.some(keyword => lowerText.includes(keyword))) {
      return 'high'
    }

    // Check for low priority keywords
    const lowKeywords = ['low priority', 'low', 'not urgent', 'kam zaroori', 'کم ضروری']
    if (lowKeywords.some(keyword => lowerText.includes(keyword))) {
      return 'low'
    }

    return 'medium'
  }

  // Clean priority keywords from text
  const cleanPriorityKeywords = (text: string): string => {
    let cleaned = text
    const patterns = [
      /\s*-\s*(high|low|medium|urgent)\s*priority\s*/gi,
      /\s*(high|low|medium|urgent)\s*priority\s*/gi,
      /\s*priority\s*:\s*(high|low|medium|urgent)\s*/gi,
      /\s*priority\s*(high|low|medium|urgent)\s*/gi,
      /\s*(فوری|ضروری)\s*/g,
      /\s*(zaroori|zaruri|fori|kam\s+zaroori)\s*/gi,
      /\s*(important\s+hai|zaruri\s+hai)\s*/gi,
    ]

    patterns.forEach(pattern => {
      cleaned = cleaned.replace(pattern, ' ')
    })

    return cleaned.replace(/\s+/g, ' ').trim()
  }

  // Auto-detect priority when title or description changes (only in create mode)
  useEffect(() => {
    if (mode === 'create' && !task) {
      const combinedText = `${title} ${description}`
      const detectedPriority = detectPriorityFromText(combinedText)

      // Only auto-set if we detect a non-medium priority
      if (detectedPriority !== 'medium' && priority === 'medium') {
        setPriority(detectedPriority)
      }
    }
  }, [title, description, mode, task])

  // Calculate remind_at based on due date and reminder option
  const calculateRemindAt = (dueDateStr: string, option: string, customStr: string): string | null => {
    if (option === 'none' || !dueDateStr) return null

    const dueDateTime = new Date(dueDateStr)

    if (option === 'custom' && customStr) {
      return new Date(customStr).toISOString()
    }

    const minutesBefore: Record<string, number> = {
      '15min': 15,
      '30min': 30,
      '1hour': 60,
      '2hours': 120,
      '1day': 1440,
    }

    if (minutesBefore[option]) {
      const remindAt = new Date(dueDateTime.getTime() - minutesBefore[option] * 60 * 1000)
      return remindAt.toISOString()
    }

    return null
  }

  // Detect reminder option from remind_at and due_date
  const detectReminderOption = (remindAt: string | null, dueDateStr: string | null): string => {
    if (!remindAt || !dueDateStr) return 'none'

    const remindTime = new Date(remindAt).getTime()
    const dueTime = new Date(dueDateStr).getTime()
    const diffMinutes = Math.round((dueTime - remindTime) / (60 * 1000))

    if (diffMinutes === 15) return '15min'
    if (diffMinutes === 30) return '30min'
    if (diffMinutes === 60) return '1hour'
    if (diffMinutes === 120) return '2hours'
    if (diffMinutes === 1440) return '1day'

    return 'custom'
  }

  // Reset form when modal opens/closes or task changes
  useEffect(() => {
    if (isOpen) {
      if (task) {
        setTitle(task.title)
        setDescription(task.description || '')
        setDueDate(
          task.due_date
            ? new Date(task.due_date).toISOString().slice(0, 16)
            : ''
        )
        setPriority(task.priority || 'medium')
        setStatus(task.status || 'pending')
        setRecurrence(task.recurrence || 'none')
        setTags(task.tags || [])

        // Set reminder option
        const detectedOption = detectReminderOption(task.remind_at, task.due_date)
        setReminderOption(detectedOption)
        if (detectedOption === 'custom' && task.remind_at) {
          setCustomReminder(new Date(task.remind_at).toISOString().slice(0, 16))
        } else {
          setCustomReminder('')
        }
      } else {
        setTitle('')
        setDescription('')
        setDueDate('')
        setReminderOption('none')
        setCustomReminder('')
        setPriority('medium')
        setStatus('pending')
        setRecurrence('none')
        setTags([])
      }
      setTagInput('')
      setErrors({})
    }
  }, [isOpen, task])

  const handleAddTag = () => {
    const trimmed = tagInput.trim()
    if (trimmed && !tags.includes(trimmed)) {
      setTags([...tags, trimmed])
      setTagInput('')
    }
  }

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove))
  }

  const handleTagKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAddTag()
    }
  }

  const validateForm = (): boolean => {
    const newErrors: typeof errors = {}

    if (!title.trim()) {
      newErrors.title = 'Title is required'
    } else if (title.length > 200) {
      newErrors.title = 'Title must be 200 characters or less'
    }

    if (description && description.length > 2000) {
      newErrors.description = 'Description must be 2000 characters or less'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    setLoading(true)
    setErrors({})

    try {
      // Clean priority keywords from title and description
      // Priority will be shown in the badge, no need to keep keywords in text
      const cleanedTitle = cleanPriorityKeywords(title.trim())
      const cleanedDescription = description.trim()
        ? cleanPriorityKeywords(description.trim())
        : null

      // Calculate remind_at from reminder option
      const remindAt = calculateRemindAt(dueDate, reminderOption, customReminder)

      const data: TaskCreate | TaskUpdate = {
        title: cleanedTitle,
        description: cleanedDescription,
        due_date: dueDate ? new Date(dueDate).toISOString() : null,
        remind_at: remindAt,
        priority,
        status,
        recurrence,
        tags: tags.length > 0 ? tags : null,
      }
      await onSubmit(data)
      onClose()
    } catch (error) {
      setErrors({
        general:
          error instanceof Error
            ? error.message
            : 'An unexpected error occurred',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={mode === 'create' ? 'Create Task' : 'Edit Task'}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-6 pb-2">
        {errors.general && (
          <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300 text-sm">
            {errors.general}
          </div>
        )}

        {/* Title */}
        <Input
          label="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          error={errors.title}
          placeholder="What needs to be done?"
          disabled={loading}
          autoFocus
        />

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Description (optional)
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Add more details..."
            rows={4}
            disabled={loading}
            className={`w-full px-4 py-3 bg-dark-card/50 backdrop-blur-xl border border-dark-border rounded-lg text-white placeholder-gray-500 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 resize-none ${
              errors.description
                ? 'border-red-500 focus:ring-red-500/50'
                : 'focus:ring-blue-500/50 focus:border-blue-500/50'
            }`}
          />
          {errors.description && (
            <p className="mt-2 text-sm text-red-400">{errors.description}</p>
          )}
          <p className="mt-2 text-xs text-gray-500">
            {description.length}/2000 characters
          </p>
        </div>

        {/* Priority and Status Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Priority
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              disabled={loading}
              className="w-full px-4 py-3 bg-dark-card/50 backdrop-blur-xl border border-dark-border rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all duration-200"
            >
              <option value="low" className="bg-dark-bg text-white">⬇️ Low</option>
              <option value="medium" className="bg-dark-bg text-white">➡️ Medium</option>
              <option value="high" className="bg-dark-bg text-white">⬆️ High</option>
              <option value="urgent" className="bg-dark-bg text-white">🔥 Urgent</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Status
            </label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              disabled={loading}
              className="w-full px-4 py-3 bg-dark-card/50 backdrop-blur-xl border border-dark-border rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all duration-200"
            >
              <option value="pending" className="bg-dark-bg text-white">⏳ Pending</option>
              <option value="in_progress" className="bg-dark-bg text-white">🔄 In Progress</option>
              <option value="completed" className="bg-dark-bg text-white">✅ Completed</option>
            </select>
          </div>
        </div>

        {/* Due Date and Recurrence Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Due Date (optional)
            </label>
            <input
              type="datetime-local"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              disabled={loading}
              className="w-full px-4 py-3 bg-dark-card/50 backdrop-blur-xl border border-dark-border rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all duration-200"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Recurrence
            </label>
            <select
              value={recurrence}
              onChange={(e) => setRecurrence(e.target.value)}
              disabled={loading}
              className="w-full px-4 py-3 bg-dark-card/50 backdrop-blur-xl border border-dark-border rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all duration-200"
            >
              <option value="none" className="bg-dark-bg text-white">🚫 None</option>
              <option value="daily" className="bg-dark-bg text-white">📅 Daily</option>
              <option value="weekly" className="bg-dark-bg text-white">📆 Weekly</option>
              <option value="monthly" className="bg-dark-bg text-white">🗓 Monthly</option>
            </select>
          </div>
        </div>

        {/* Reminder Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              🔔 Reminder
            </label>
            <select
              value={reminderOption}
              onChange={(e) => setReminderOption(e.target.value)}
              disabled={loading || !dueDate}
              className="w-full px-4 py-3 bg-dark-card/50 backdrop-blur-xl border border-dark-border rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 disabled:opacity-50 transition-all duration-200"
            >
              <option value="none" className="bg-dark-bg text-white">🚫 No Reminder</option>
              <option value="15min" className="bg-dark-bg text-white">⏰ 15 minutes before</option>
              <option value="30min" className="bg-dark-bg text-white">⏰ 30 minutes before</option>
              <option value="1hour" className="bg-dark-bg text-white">⏰ 1 hour before</option>
              <option value="2hours" className="bg-dark-bg text-white">⏰ 2 hours before</option>
              <option value="1day" className="bg-dark-bg text-white">⏰ 1 day before</option>
              <option value="custom" className="bg-dark-bg text-white">📝 Custom time</option>
            </select>
            {!dueDate && (
              <p className="mt-2 text-xs text-gray-500">Set a due date first to enable reminders</p>
            )}
          </div>

          {reminderOption === 'custom' && (
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Custom Reminder Time
              </label>
              <input
                type="datetime-local"
                value={customReminder}
                onChange={(e) => setCustomReminder(e.target.value)}
                disabled={loading}
                className="w-full px-4 py-3 bg-dark-card/50 backdrop-blur-xl border border-dark-border rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all duration-200"
              />
            </div>
          )}
        </div>

        {/* Tags Section */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Tags (optional)
          </label>
          <div className="flex gap-3 mb-3">
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={handleTagKeyDown}
              placeholder="Add a tag (e.g., Work, Home, Personal)"
              disabled={loading}
              className="flex-1 px-4 py-3 bg-dark-card/50 backdrop-blur-xl border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all duration-200"
            />
            <Button
              type="button"
              onClick={handleAddTag}
              disabled={loading || !tagInput.trim()}
              variant="secondary"
            >
              Add
            </Button>
          </div>
          {tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {tags.map((tag, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-indigo-500/20 text-indigo-300 border border-indigo-500/50 rounded-full text-sm flex items-center gap-2"
                >
                  <span>🏷 {tag}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveTag(tag)}
                    className="hover:text-indigo-100 text-xs font-bold"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-end gap-3 pt-6 border-t border-dark-border sticky bottom-0 bg-dark-card z-10 -mx-6 px-6">
          <Button
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button type="submit" loading={loading}>
            {mode === 'create' ? 'Create Task' : 'Save Changes'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
