/**
 * GAIU 4 - Mode Urgence
 * Page: /app/(dashboard)/urgence/page.tsx
 * 
 * Interface dédiée pour gérer les tâches urgentes
 * avec actions rapides et priorités visuelles
 */

"use client";

import { useState, useEffect } from "react";
import { Task, TaskPriority, UrgenceTask, UrgenceAction } from "@/types/task";
import { useTasks } from "@/lib/hooks/useTasks";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { ProgressBar } from "@/components/dashboard/ProgressBar";
import {
  AlertTriangle,
  Clock,
  FileWarning,
  CheckCircle,
  ArrowRight,
  Upload,
  Send,
  X,
} from "lucide-react";

export default function UrgencePage() {
  const { tasks, uploadDocument, submitTask } = useTasks();
  const [selectedTask, setSelectedTask] = useState<string | null>(null);
  
  const urgentTasks = tasks
    .filter((task) => task.priority === TaskPriority.URGENT)
    .map((task) => enhanceUrgentTask(task))
    .sort((a, b) => a.daysUntilDeadline - b.daysUntilDeadline);

  useEffect(() => {
    // Auto-select la tâche la plus urgente
    if (urgentTasks.length > 0 && !selectedTask) {
      setSelectedTask(urgentTasks[0].task.id);
    }
  }, [urgentTasks, selectedTask]);

  const selectedUrgentTask = urgentTasks.find(
    (ut) => ut.task.id === selectedTask
  );

  if (urgentTasks.length === 0) {
    return <NoUrgentTasksView />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 dark:from-red-950 dark:to-orange-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header avec alerte */}
        <div className="mb-8">
          <div className="bg-red-100 dark:bg-red-900 border-l-4 border-red-500 p-6 rounded-lg">
            <div className="flex items-start">
              <AlertTriangle className="w-8 h-8 text-red-600 dark:text-red-400 mr-4 flex-shrink-0 animate-pulse" />
              <div className="flex-1">
                <h1 className="text-2xl font-bold text-red-900 dark:text-red-100 mb-2">
                  ⚡ Mode Urgence Activé
                </h1>
                <p className="text-red-700 dark:text-red-300">
                  Vous avez <strong>{urgentTasks.length}</strong> démarche(s) critique(s) 
                  nécessitant une attention immédiate
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => window.location.href = "/"}
                className="ml-4"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>

        {/* Layout principal */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Liste des tâches urgentes - Sidebar */}
          <div className="lg:col-span-1">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4">
              Tâches Critiques
            </h2>
            
            <div className="space-y-3">
              {urgentTasks.map((urgentTask) => (
                <UrgentTaskCard
                  key={urgentTask.task.id}
                  urgentTask={urgentTask}
                  isSelected={selectedTask === urgentTask.task.id}
                  onSelect={() => setSelectedTask(urgentTask.task.id)}
                />
              ))}
            </div>
          </div>

          {/* Détails et actions - Main */}
          <div className="lg:col-span-2">
            {selectedUrgentTask ? (
              <UrgentTaskDetails
                urgentTask={selectedUrgentTask}
                onUploadDocument={uploadDocument}
                onSubmit={submitTask}
              />
            ) : (
              <Card className="p-12 text-center">
                <p className="text-slate-600 dark:text-slate-400">
                  Sélectionnez une tâche pour voir les détails
                </p>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// COMPONENTS
// ============================================================================

interface UrgentTaskCardProps {
  urgentTask: UrgenceTask;
  isSelected: boolean;
  onSelect: () => void;
}

function UrgentTaskCard({ urgentTask, isSelected, onSelect }: UrgentTaskCardProps) {
  const { task, daysUntilDeadline, missingDocuments } = urgentTask;
  
  const isOverdue = daysUntilDeadline < 0;
  const isDueToday = daysUntilDeadline === 0;

  return (
    <Card
      onClick={onSelect}
      className={`
        p-4 cursor-pointer transition-all
        ${isSelected ? 'ring-2 ring-red-500 bg-red-50 dark:bg-red-900' : 'hover:bg-slate-50 dark:hover:bg-slate-800'}
        ${isOverdue ? 'border-red-500' : ''}
      `}
    >
      <div className="flex items-start justify-between mb-3">
        <h3 className="font-semibold text-slate-900 dark:text-white text-sm line-clamp-2">
          {task.title}
        </h3>
        
        {isOverdue ? (
          <Badge variant="danger" size="sm" className="ml-2 flex-shrink-0">
            Dépassée
          </Badge>
        ) : isDueToday ? (
          <Badge variant="warning" size="sm" className="ml-2 flex-shrink-0">
            Aujourd'hui
          </Badge>
        ) : (
          <Badge variant="danger" size="sm" className="ml-2 flex-shrink-0">
            {daysUntilDeadline}j
          </Badge>
        )}
      </div>

      <div className="flex items-center gap-4 text-xs text-slate-600 dark:text-slate-400">
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          <span>{urgentTask.estimatedTimeToComplete} min</span>
        </div>
        
        {missingDocuments.length > 0 && (
          <div className="flex items-center gap-1 text-orange-600 dark:text-orange-400">
            <FileWarning className="w-3 h-3" />
            <span>{missingDocuments.length} doc(s)</span>
          </div>
        )}
      </div>

      <ProgressBar
        progress={task.progress}
        variant={task.progress < 50 ? "danger" : "warning"}
        className="mt-3 h-1"
        showLabel={false}
      />
    </Card>
  );
}

interface UrgentTaskDetailsProps {
  urgentTask: UrgenceTask;
  onUploadDocument: (taskId: string, file: File) => Promise<void>;
  onSubmit: (taskId: string) => Promise<void>;
}

function UrgentTaskDetails({ urgentTask, onUploadDocument, onSubmit }: UrgentTaskDetailsProps) {
  const { task, daysUntilDeadline, missingDocuments, actions } = urgentTask;
  const [completedActions, setCompletedActions] = useState<Set<string>>(new Set());

  const handleActionComplete = (actionId: string) => {
    setCompletedActions(new Set([...completedActions, actionId]));
  };

  const allActionsCompleted = actions.every((action) =>
    completedActions.has(action.id)
  );

  const totalTime = actions.reduce((sum, action) => sum + action.estimatedTime, 0);
  const completedTime = actions
    .filter((action) => completedActions.has(action.id))
    .reduce((sum, action) => sum + action.estimatedTime, 0);

  return (
    <div className="space-y-6">
      
      {/* En-tête de la tâche */}
      <Card className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
              {task.title}
            </h2>
            <p className="text-slate-600 dark:text-slate-400">
              {task.description}
            </p>
          </div>
          
          <DeadlineBadge daysUntilDeadline={daysUntilDeadline} />
        </div>

        <div className="flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-slate-500" />
            <span className="text-slate-700 dark:text-slate-300">
              Temps estimé: <strong>{totalTime} minutes</strong>
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-slate-500" />
            <span className="text-slate-700 dark:text-slate-300">
              Progression: <strong>{Math.round(task.progress)}%</strong>
            </span>
          </div>
        </div>

        <ProgressBar
          progress={(completedTime / totalTime) * 100}
          variant="primary"
          className="mt-4"
          showLabel={true}
        />
      </Card>

      {/* Actions à réaliser */}
      <Card className="p-6">
        <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">
          Actions Requises
        </h3>

        <div className="space-y-3">
          {actions
            .sort((a, b) => a.priority - b.priority)
            .map((action, index) => (
              <ActionItem
                key={action.id}
                action={action}
                index={index + 1}
                isCompleted={completedActions.has(action.id)}
                onComplete={() => handleActionComplete(action.id)}
              />
            ))}
        </div>
      </Card>

      {/* Documents manquants */}
      {missingDocuments.length > 0 && (
        <Card className="p-6 border-orange-200 dark:border-orange-800">
          <div className="flex items-start gap-3 mb-4">
            <FileWarning className="w-6 h-6 text-orange-500 flex-shrink-0" />
            <div>
              <h3 className="font-bold text-slate-900 dark:text-white mb-1">
                Documents Manquants
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Ces documents sont requis pour compléter la démarche
              </p>
            </div>
          </div>

          <div className="space-y-2">
            {missingDocuments.map((docType) => (
              <div
                key={docType}
                className="flex items-center justify-between p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg"
              >
                <span className="text-sm font-medium text-slate-900 dark:text-white">
                  {getDocumentLabel(docType)}
                </span>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => {
                    const input = document.createElement("input");
                    input.type = "file";
                    input.onchange = async (e) => {
                      const file = (e.target as HTMLInputElement).files?.[0];
                      if (file) {
                        await onUploadDocument(task.id, file);
                        handleActionComplete(`upload_${docType}`);
                      }
                    };
                    input.click();
                  }}
                >
                  <Upload className="w-4 h-4 mr-1" />
                  Uploader
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Bouton de soumission */}
      <Card className="p-6 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-900 dark:text-white mb-1">
              Prêt à Soumettre ?
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {allActionsCompleted
                ? "Toutes les actions sont complétées"
                : `Il reste ${actions.length - completedActions.size} action(s)`}
            </p>
          </div>

          <Button
            variant="success"
            size="lg"
            disabled={!allActionsCompleted}
            onClick={() => onSubmit(task.id)}
          >
            <Send className="w-5 h-5 mr-2" />
            Soumettre Maintenant
          </Button>
        </div>
      </Card>
    </div>
  );
}

function ActionItem({
  action,
  index,
  isCompleted,
  onComplete,
}: {
  action: UrgenceAction;
  index: number;
  isCompleted: boolean;
  onComplete: () => void;
}) {
  return (
    <div
      className={`
        flex items-center gap-4 p-4 rounded-lg border-2 transition-all
        ${isCompleted 
          ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' 
          : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700'
        }
      `}
    >
      <div className={`
        w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0
        ${isCompleted 
          ? 'bg-green-500 text-white' 
          : 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300'
        }
      `}>
        {isCompleted ? <CheckCircle className="w-5 h-5" /> : index}
      </div>

      <div className="flex-1">
        <h4 className={`font-semibold ${isCompleted ? 'line-through text-slate-500' : 'text-slate-900 dark:text-white'}`}>
          {action.label}
        </h4>
        <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
          ⏱️ {action.estimatedTime} minutes
        </p>
      </div>

      {!isCompleted && (
        <Button
          variant="outline"
          size="sm"
          onClick={onComplete}
        >
          Marquer comme fait
        </Button>
      )}
    </div>
  );
}

function DeadlineBadge({ daysUntilDeadline }: { daysUntilDeadline: number }) {
  if (daysUntilDeadline < 0) {
    return (
      <Badge variant="danger" size="lg" className="animate-pulse">
        ⚠️ Dépassée de {Math.abs(daysUntilDeadline)} jour(s)
      </Badge>
    );
  }

  if (daysUntilDeadline === 0) {
    return (
      <Badge variant="warning" size="lg" className="animate-pulse">
        ⏰ Échéance Aujourd'hui
      </Badge>
    );
  }

  return (
    <Badge variant="danger" size="lg">
      ⏱️ {daysUntilDeadline} jour(s) restant(s)
    </Badge>
  );
}

function NoUrgentTasksView() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950 dark:to-emerald-950 flex items-center justify-center p-8">
      <Card className="max-w-md p-12 text-center">
        <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-6" />
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">
          Aucune Urgence !
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mb-6">
          Toutes vos démarches sont à jour. Vous pouvez vous détendre ! 🎉
        </p>
        <Button
          variant="primary"
          onClick={() => window.location.href = "/"}
        >
          Retour au Dashboard
        </Button>
      </Card>
    </div>
  );
}

// ============================================================================
// HELPERS
// ============================================================================

function enhanceUrgentTask(task: Task): UrgenceTask {
  const deadline = task.deadline ? new Date(task.deadline) : null;
  const now = new Date();
  const daysUntilDeadline = deadline
    ? Math.ceil((deadline.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
    : 999;

  const missingDocuments = task.requiredDocuments.filter(
    (doc) => !task.submittedDocuments.some((submitted) => submitted.documentType === doc)
  );

  const actions: UrgenceAction[] = [
    ...missingDocuments.map((doc, i) => ({
      id: `upload_${doc}`,
      label: `Uploader ${getDocumentLabel(doc)}`,
      icon: "upload",
      priority: i + 1,
      completed: false,
      estimatedTime: 5,
    })),
    {
      id: "review",
      label: "Vérifier les informations",
      icon: "check",
      priority: 100,
      completed: task.progress > 80,
      estimatedTime: 10,
    },
  ];

  return {
    task,
    daysUntilDeadline,
    missingDocuments,
    estimatedTimeToComplete: actions.reduce((sum, a) => sum + a.estimatedTime, 0),
    actions,
  };
}

function getDocumentLabel(docType: string): string {
  const labels: Record<string, string> = {
    avis_imposition: "Avis d'Imposition",
    feuille_soins: "Feuille de Soins",
    carte_grise: "Carte Grise",
    justificatif_domicile: "Justificatif de Domicile",
    bulletin_salaire: "Bulletin de Salaire",
  };
  return labels[docType] || docType;
}
