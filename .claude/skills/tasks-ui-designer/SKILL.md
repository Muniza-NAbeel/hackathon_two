---
name: tasks-ui-designer
description: Design and improve the Tasks page UI for the Todo app. Trigger when user asks about task page layout, sidebar, filters, sorting, task cards, or UI design improvements.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

# Tasks UI Designer Skill

Expert guidance for designing and improving the Tasks page UI in the Todo Full-Stack Web Application.

## Tech Stack

- **Frontend:** Next.js 14+ with TypeScript
- **Styling:** Tailwind CSS with custom theme
- **Theme:** Dark mode with neon accents (cyan, purple, blue)
- **Components:** Custom React components

## Project Structure

```
phase_3/frontend/
├── components/
│   ├── tasks/
│   │   ├── EnhancedTaskCard.tsx    # Individual task card
│   │   ├── EnhancedTaskForm.tsx    # Add/Edit task form
│   │   ├── LeftSidebar.tsx         # Filters sidebar
│   │   ├── SearchBar.tsx           # Search component
│   │   ├── HeaderSummary.tsx       # Stats header
│   │   └── EmptyState.tsx          # No tasks view
│   └── ui/
│       ├── Button.tsx
│       ├── Input.tsx
│       ├── Modal.tsx
│       └── Navbar.tsx
├── app/(dashboard)/
│   ├── dashboard/page.tsx
│   └── tasks-enhanced/page.tsx
└── styles/
    └── globals.css
```

## Design System

### Colors (Tailwind Classes)

```
Primary:      neon-cyan (#00f5d4)
Secondary:    neon-purple (#9b5de5)
Accent:       neon-blue (#00bbf9)
Background:   dark-bg (#0a0a0f)
Card:         dark-card (#12121a)
Border:       dark-border (#1e1e2e)
```

### Common Patterns

```tsx
// Card styling
className="bg-dark-card/40 backdrop-blur-xl rounded-xl border border-dark-border"

// Hover effects
className="hover:shadow-neon-cyan/20 hover:-translate-y-1 transition-all"

// Gradient text
className="bg-gradient-to-r from-neon-purple to-neon-cyan bg-clip-text text-transparent"

// Neon glow
className="shadow-lg shadow-neon-cyan/30"
```

## UI Components Guidelines

### 1. Task Card Design

```tsx
// Priority color strip on left
<div className="absolute left-0 top-0 bottom-0 w-1 bg-{priority-color}" />

// Priority badges
low:    "bg-gray-500/20 text-gray-300"
medium: "bg-blue-500/20 text-blue-300"
high:   "bg-orange-500/20 text-orange-300"
urgent: "bg-red-500/20 text-red-300"

// Completion checkbox
<button className="w-6 h-6 rounded-lg bg-white/5 hover:bg-white/10 ring-1 ring-white/20" />
// Completed state
<button className="bg-green-500 shadow-md shadow-green-500/30" />
```

### 2. Sidebar Filters

```tsx
// Filter section
<div className="space-y-2">
  <h3 className="text-xs font-semibold text-gray-400 uppercase">Status</h3>
  <button className="w-full text-left px-3 py-2 rounded-lg hover:bg-dark-border/50" />
</div>

// Active filter
className="bg-neon-cyan/10 text-neon-cyan border-l-2 border-neon-cyan"
```

### 3. Search Bar

```tsx
<input
  className="w-full px-4 py-3 bg-dark-card border border-dark-border rounded-lg
             text-white placeholder-gray-500 focus:border-neon-cyan focus:outline-none"
/>
```

### 4. Empty State

```tsx
<div className="flex flex-col items-center justify-center py-12">
  <Icon className="w-16 h-16 text-gray-600 mb-4" />
  <h3 className="text-xl font-medium text-gray-300">No tasks yet</h3>
  <p className="text-gray-500">Create your first task to get started</p>
</div>
```

## Responsive Design

```tsx
// Mobile-first approach
className="p-3 sm:p-4 md:p-5"           // Padding
className="text-sm sm:text-base"         // Text size
className="gap-2 sm:gap-3 md:gap-4"      // Spacing
className="hidden sm:block"              // Hide on mobile
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3"  // Grid
```

## Animation Classes

```tsx
// Smooth transitions
className="transition-all duration-300"

// Hover lift effect
className="hover:-translate-y-1"

// Pulse for loading
className="animate-pulse"

// Bounce for dots
className="animate-bounce"
```

## Best Practices

1. **Consistency:** Use existing color variables and patterns
2. **Accessibility:** Include aria-labels, focus states
3. **Performance:** Use React.memo for heavy components
4. **Mobile-first:** Design for small screens first
5. **Dark theme:** Ensure sufficient contrast
6. **Feedback:** Show loading states, success/error messages

## Common Tasks

### Add new filter option
1. Update LeftSidebar.tsx
2. Add filter state to parent
3. Apply filter logic to task list

### Modify task card layout
1. Edit EnhancedTaskCard.tsx
2. Follow priority color patterns
3. Test responsive breakpoints

### Add new UI element
1. Create component in appropriate folder
2. Use existing Tailwind classes
3. Follow dark theme patterns
