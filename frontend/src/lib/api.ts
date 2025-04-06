import axios from 'axios';
import { Plugin, PluginUpdate } from '@/types/plugin';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getPlugins = async (): Promise<Plugin[]> => {
  try {
    const response = await api.get<Plugin[]>('/plugins/');
    return response.data;
  } catch (error) {
    console.error('Error fetching plugins:', error);
    throw error;
  }
};

export const getPlugin = async (id: string): Promise<Plugin> => {
  try {
    const response = await api.get<Plugin>(`/plugins/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching plugin ${id}:`, error);
    throw error;
  }
};

export const createPlugin = async (plugin: Plugin): Promise<Plugin> => {
  try {
    const response = await api.post<Plugin>('/plugins/', plugin);
    return response.data;
  } catch (error) {
    console.error('Error creating plugin:', error);
    throw error;
  }
};

export const updatePlugin = async (id: string, plugin: PluginUpdate): Promise<Plugin> => {
  try {
    const response = await api.put<Plugin>(`/plugins/${id}`, plugin);
    return response.data;
  } catch (error) {
    console.error(`Error updating plugin ${id}:`, error);
    throw error;
  }
};

export const deletePlugin = async (id: string): Promise<void> => {
  try {
    await api.delete(`/plugins/${id}`);
  } catch (error) {
    console.error(`Error deleting plugin ${id}:`, error);
    throw error;
  }
}; 