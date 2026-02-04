/**
 * GAIU 4 - Frontend Type Definitions
 * Types TypeScript pour l'ensemble de l'application
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum TaskState {
  CREATED = "created",
  PENDING = "pending",
  IN_PROGRESS = "in_progress",
  AWAITING_DOCUMENTS = "awaiting_documents",
  UNDER_REVIEW = "under_review",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

export enum TaskPriority {
  URGENT = "urgent",
  HIGH = "high",
  MEDIUM = "medium",
  LOW = "low",
}

export enum AgentType {
  FISCAL = "fiscal",
  HEALTH = "health",
  MOBILITY = "mobility",
  HOUSING = "housing",
  EMPLOYMENT = "employment",
}

export enum DocumentType {
  AVIS_IMPOSITION = "avis_imposition",
  FEUILLE_SOINS = "feuille_soins",
  CARTE_GRISE = "carte_grise",
  JUSTIFICATIF_DOMICILE = "justificatif_domicile",
  BULLETIN_SALAIRE = "bulletin_salaire",
  PERMIS_CONDUIRE = "permis_conduire",
  CARTE_IDENTITE = "carte_identite",
}

// ============================================================================
// USER & AUTH
// ============================================================================

export interface User {
  id: string;
  username: string | null;
  fcSub: string;
  status: "active" | "suspended" | "pending_verification";
  createdAt: string;
  lastLoginAt: string | null;
  preferences: UserPreferences;
}

export interface UserPreferences {
  theme: "light" | "dark" | "auto";
  notifications: {
    email: boolean;
    sms: boolean;
    push: boolean;
  };
  language: "fr" | "en";
}

export interface AuthSession {
  sessionId: string;
  user: User;
  authLevel: "basic" | "substantial" | "high";
  expiresAt: string;
}

// ============================================================================
// TASKS
// ============================================================================

export interface Task {
  id: string;
  userId: string;
  title: string;
  description: string;
  agentType: AgentType;
  state: TaskState;
  priority: TaskPriority;
  progress: number;
  createdAt: string;
  updatedAt: string;
  deadline: string | null;
  completedAt: string | null;
  metadata: Record<string, any>;
  errorMessage: string | null;
  requiredDocuments: string[];
  submittedDocuments: Document[];
}

export interface TaskStateTransition {
  id: number;
  taskId: string;
  fromState: TaskState | null;
  toState: TaskState;
  transitionedAt: string;
  transitionedBy: "system" | "user";
  context: Record<string, any>;
}

export interface CreateTaskRequest {
  title: string;
  description: string;
  agentType: AgentType;
  deadline?: string;
  requiredDocuments: string[];
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  priority?: TaskPriority;
  deadline?: string;
}

// ============================================================================
// DOCUMENTS
// ============================================================================

export interface Document {
  id: string;
  userId: string;
  documentType: DocumentType;
  originalFilename: string;
  mimeType: string;
  fileSize: number;
  pageCount: number;
  vaultRecordId: string;
  ocrStatus: "pending" | "processing" | "completed" | "failed";
  ocrConfidence: number | null;
  extractedData: Record<string, any>;
  uploadedAt: string;
  processedAt: string | null;
  isValid: boolean;
  validationErrors: string[];
}

export interface UploadDocumentRequest {
  file: File;
  documentType: DocumentType;
  taskId?: string;
}

// ============================================================================
// TIMELINE
// ============================================================================

export interface TimelineEvent {
  id: string;
  timestamp: string;
  type: "task_created" | "task_updated" | "document_uploaded" | "task_completed" | "task_failed";
  title: string;
  description: string;
  icon: string;
  color: string;
  metadata: Record<string, any>;
}

// ============================================================================
// DASHBOARD STATS
// ============================================================================

export interface DashboardStats {
  totalTasks: number;
  activeTasks: number;
  completedTasks: number;
  urgentTasks: number;
  documentsUploaded: number;
  averageProgress: number;
  tasksByState: Record<TaskState, number>;
  tasksByAgent: Record<AgentType, number>;
  recentActivity: TimelineEvent[];
}

// ============================================================================
// API RESPONSES
// ============================================================================

export interface APIResponse<T = any> {
  success: boolean;
  data: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  metadata?: {
    timestamp: string;
    requestId: string;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

// ============================================================================
// UI COMPONENT PROPS
// ============================================================================

export interface TaskCardProps {
  task: Task;
  onViewDetails: (taskId: string) => void;
  onCancel?: (taskId: string) => void;
}

export interface StatusBadgeProps {
  state: TaskState;
  size?: "sm" | "md" | "lg";
}

export interface PriorityBadgeProps {
  priority: TaskPriority;
  size?: "sm" | "md" | "lg";
}

export interface ProgressBarProps {
  progress: number;
  showLabel?: boolean;
  variant?: "primary" | "success" | "warning" | "danger";
}

export interface TimelineProps {
  events: TimelineEvent[];
  maxEvents?: number;
}

// ============================================================================
// FORMS
// ============================================================================

export interface TaskFormData {
  title: string;
  description: string;
  agentType: AgentType;
  priority: TaskPriority;
  deadline: string | null;
  requiredDocuments: DocumentType[];
}

export interface DocumentUploadFormData {
  documentType: DocumentType;
  file: File | null;
}

// ============================================================================
// NOTIFICATION
// ============================================================================

export interface Notification {
  id: string;
  type: "success" | "error" | "warning" | "info";
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actionUrl?: string;
}

// ============================================================================
// URGENCE MODE
// ============================================================================

export interface UrgenceTask {
  task: Task;
  daysUntilDeadline: number;
  missingDocuments: DocumentType[];
  estimatedTimeToComplete: number; // minutes
  actions: UrgenceAction[];
}

export interface UrgenceAction {
  id: string;
  label: string;
  icon: string;
  priority: number;
  completed: boolean;
  estimatedTime: number; // minutes
}

// ============================================================================
// FILTERS & SORTING
// ============================================================================

export interface TaskFilters {
  state?: TaskState[];
  priority?: TaskPriority[];
  agentType?: AgentType[];
  dateFrom?: string;
  dateTo?: string;
  search?: string;
}

export interface SortOptions {
  field: "createdAt" | "updatedAt" | "deadline" | "priority" | "progress";
  order: "asc" | "desc";
}
