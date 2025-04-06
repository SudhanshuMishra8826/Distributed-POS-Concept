export interface Plugin {
  id: string;
  active: boolean;
  filters: Record<string, any> | null;
  actions: Record<string, any> | null;
}

export interface PluginUpdate {
  active?: boolean;
  filters?: Record<string, any>;
  actions?: Record<string, any>;
} 