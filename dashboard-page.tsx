/**
 * GAIU 4 - Dashboard Principal
 * Page: /app/(dashboard)/page.tsx
 */

"use client";

import { useState, useEffect } from "react";
import { Task, TaskState, TaskPriority, DashboardStats, TimelineEvent } from "@/types/task";
import { useTasks } from "@/lib/hooks/useTasks";
import { StatusCard } from "@/components/dashboard/StatusCard";
import { TaskList } from "@/components/dashboard/TaskList";
import { ProgressBar } from "@/components/dashboard/ProgressBar";
import { Timeline } from "@/components/ui/Timeline";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { 
  AlertCircle, 
  CheckCircle, 
  Clock, 
  FileText, 
  TrendingUp,
  Zap
} from "lucide-react";

export default function DashboardPage() {
  const { tasks, stats, isLoading, refreshTasks } = useTasks();
  const [showUrgentOnly, setShowUrgentOnly] = useState(false);

  useEffect(() => {
    // Refresh automatique toutes les 30 secondes
    const interval = setInterval(refreshTasks, 30000);
    return () => clearInterval(interval);
  }, [refreshTasks]);

  const urgentTasks = tasks.filter(
    (task) => task.priority === TaskPriority.URGENT && task.state !== TaskState.COMPLETED
  );

  const activeTasks = tasks.filter(
    (task) => 
      task.state !== TaskState.COMPLETED && 
      task.state !== TaskState.CANCELLED
  );

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header avec mode urgence */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                Tableau de Bord
              </h1>
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                Vue d'ensemble de vos démarches administratives
              </p>
            </div>

            {urgentTasks.length > 0 && (
              <Button
                variant="danger"
                size="lg"
                onClick={() => window.location.href = "/urgence"}
                className="flex items-center gap-2 animate-pulse"
              >
                <Zap className="w-5 h-5" />
                Mode Urgence ({urgentTasks.length})
              </Button>
            )}
          </div>
        </div>

        {/* Cartes de statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatusCard
            title="Tâches Actives"
            value={activeTasks.length}
            icon={<Clock className="w-6 h-6" />}
            color="blue"
            trend={stats.totalTasks > 0 ? "+12%" : undefined}
          />

          <StatusCard
            title="Complétées"
            value={stats.completedTasks}
            icon={<CheckCircle className="w-6 h-6" />}
            color="green"
            trend={stats.completedTasks > 0 ? "+8%" : undefined}
          />

          <StatusCard
            title="Urgentes"
            value={urgentTasks.length}
            icon={<AlertCircle className="w-6 h-6" />}
            color="red"
            pulse={urgentTasks.length > 0}
          />

          <StatusCard
            title="Documents"
            value={stats.documentsUploaded}
            icon={<FileText className="w-6 h-6" />}
            color="purple"
          />
        </div>

        {/* Progression globale */}
        {activeTasks.length > 0 && (
          <Card className="mb-8 p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                  Progression Globale
                </h3>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Moyenne de toutes vos démarches en cours
                </p>
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-500" />
                <span className="text-2xl font-bold text-slate-900 dark:text-white">
                  {Math.round(stats.averageProgress)}%
                </span>
              </div>
            </div>
            <ProgressBar 
              progress={stats.averageProgress} 
              showLabel={false}
              variant="primary"
              className="h-3"
            />
          </Card>
        )}

        {/* Layout principal : Tâches + Timeline */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Liste des tâches - 2/3 */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
                Mes Démarches
              </h2>
              
              <div className="flex gap-2">
                <Button
                  variant={showUrgentOnly ? "primary" : "outline"}
                  size="sm"
                  onClick={() => setShowUrgentOnly(!showUrgentOnly)}
                >
                  {showUrgentOnly ? "Toutes" : "Urgentes"}
                </Button>
                
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => window.location.href = "/tasks/new"}
                >
                  + Nouvelle
                </Button>
              </div>
            </div>

            <TaskList
              tasks={showUrgentOnly ? urgentTasks : activeTasks}
              emptyMessage={
                showUrgentOnly
                  ? "Aucune tâche urgente"
                  : "Aucune démarche en cours"
              }
            />
          </div>

          {/* Timeline - 1/3 */}
          <div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">
              Activité Récente
            </h2>
            
            <Timeline events={stats.recentActivity} maxEvents={10} />
            
            {/* Répartition par état */}
            <Card className="mt-6 p-4">
              <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-4">
                Répartition par État
              </h3>
              
              <div className="space-y-3">
                {Object.entries(stats.tasksByState).map(([state, count]) => (
                  count > 0 && (
                    <div key={state} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${getStateColor(state as TaskState)}`} />
                        <span className="text-sm text-slate-600 dark:text-slate-400">
                          {getStateLabel(state as TaskState)}
                        </span>
                      </div>
                      <Badge variant="secondary" size="sm">
                        {count}
                      </Badge>
                    </div>
                  )
                ))}
              </div>
            </Card>

            {/* Répartition par agent */}
            <Card className="mt-6 p-4">
              <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-4">
                Par Domaine
              </h3>
              
              <div className="space-y-3">
                {Object.entries(stats.tasksByAgent).map(([agent, count]) => (
                  count > 0 && (
                    <div key={agent} className="flex items-center justify-between">
                      <span className="text-sm text-slate-600 dark:text-slate-400">
                        {getAgentLabel(agent)}
                      </span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-blue-500"
                            style={{ width: `${(count / stats.totalTasks) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-slate-900 dark:text-white">
                          {count}
                        </span>
                      </div>
                    </div>
                  )
                ))}
              </div>
            </Card>
          </div>
        </div>

        {/* Message d'aide si aucune tâche */}
        {tasks.length === 0 && (
          <Card className="mt-8 p-12 text-center">
            <div className="max-w-md mx-auto">
              <FileText className="w-16 h-16 mx-auto mb-4 text-slate-400" />
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                Aucune démarche en cours
              </h3>
              <p className="text-slate-600 dark:text-slate-400 mb-6">
                Commencez par créer votre première démarche administrative automatisée
              </p>
              <Button
                variant="primary"
                size="lg"
                onClick={() => window.location.href = "/tasks/new"}
              >
                Créer ma première démarche
              </Button>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function getStateColor(state: TaskState): string {
  const colors: Record<TaskState, string> = {
    [TaskState.CREATED]: "bg-slate-400",
    [TaskState.PENDING]: "bg-blue-400",
    [TaskState.IN_PROGRESS]: "bg-yellow-400",
    [TaskState.AWAITING_DOCUMENTS]: "bg-orange-400",
    [TaskState.UNDER_REVIEW]: "bg-purple-400",
    [TaskState.COMPLETED]: "bg-green-400",
    [TaskState.FAILED]: "bg-red-400",
    [TaskState.CANCELLED]: "bg-slate-400",
  };
  return colors[state] || "bg-slate-400";
}

function getStateLabel(state: TaskState): string {
  const labels: Record<TaskState, string> = {
    [TaskState.CREATED]: "Créée",
    [TaskState.PENDING]: "En attente",
    [TaskState.IN_PROGRESS]: "En cours",
    [TaskState.AWAITING_DOCUMENTS]: "Documents manquants",
    [TaskState.UNDER_REVIEW]: "En vérification",
    [TaskState.COMPLETED]: "Terminée",
    [TaskState.FAILED]: "Échouée",
    [TaskState.CANCELLED]: "Annulée",
  };
  return labels[state] || state;
}

function getAgentLabel(agent: string): string {
  const labels: Record<string, string> = {
    fiscal: "📋 Fiscal",
    health: "🏥 Santé",
    mobility: "🚗 Mobilité",
    housing: "🏠 Logement",
    employment: "💼 Emploi",
  };
  return labels[agent] || agent;
}

// ============================================================================
// LOADING SKELETON
// ============================================================================

function DashboardSkeleton() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 p-8">
      <div className="max-w-7xl mx-auto space-y-8 animate-pulse">
        <div className="h-12 bg-slate-200 dark:bg-slate-700 rounded w-1/3" />
        
        <div className="grid grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-slate-200 dark:bg-slate-700 rounded-lg" />
          ))}
        </div>
        
        <div className="h-24 bg-slate-200 dark:bg-slate-700 rounded-lg" />
        
        <div className="grid grid-cols-3 gap-8">
          <div className="col-span-2 space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 bg-slate-200 dark:bg-slate-700 rounded-lg" />
            ))}
          </div>
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-16 bg-slate-200 dark:bg-slate-700 rounded-lg" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
