'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import Header from '@/components/Header';
import PluginCard from '@/components/PluginCard';
import { Plugin } from '@/types/plugin';
import { getPlugins, updatePlugin, deletePlugin } from '@/lib/api';

export default function Home() {
    const [plugins, setPlugins] = useState<Plugin[]>([]);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        fetchPlugins();
    }, []);

    const fetchPlugins = async () => {
        try {
            setLoading(true);
            const data = await getPlugins();
            setPlugins(data);
        } catch (error) {
            toast.error('Failed to fetch plugins');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleToggleStatus = async (id: string, active: boolean) => {
        try {
            await updatePlugin(id, { active });
            setPlugins(plugins.map(plugin =>
                plugin.id === id ? { ...plugin, active } : plugin
            ));
            toast.success(`Plugin ${active ? 'activated' : 'deactivated'} successfully`);
        } catch (error) {
            toast.error(`Failed to ${active ? 'activate' : 'deactivate'} plugin`);
            console.error(error);
        }
    };

    const handleDelete = async (id: string) => {
        try {
            await deletePlugin(id);
            setPlugins(plugins.filter(plugin => plugin.id !== id));
            toast.success('Plugin deleted successfully');
        } catch (error) {
            toast.error('Failed to delete plugin');
            console.error(error);
        }
    };

    return (
        <main className="min-h-screen bg-gray-50">
            <Header />

            <div className="container mx-auto px-4 py-8">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold text-gray-800">Plugins</h1>
                    <button
                        onClick={() => router.push('/create')}
                        className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                        Create New Plugin
                    </button>
                </div>

                {loading ? (
                    <div className="flex justify-center items-center h-64">
                        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
                    </div>
                ) : plugins.length === 0 ? (
                    <div className="text-center py-12 bg-white rounded-lg shadow">
                        <h3 className="text-lg font-medium text-gray-900">No plugins found</h3>
                        <p className="mt-1 text-sm text-gray-500">Get started by creating a new plugin.</p>
                        <div className="mt-6">
                            <button
                                onClick={() => router.push('/create')}
                                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                            >
                                Create New Plugin
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {plugins.map(plugin => (
                            <PluginCard
                                key={plugin.id}
                                plugin={plugin}
                                onDelete={handleDelete}
                                onToggleStatus={handleToggleStatus}
                            />
                        ))}
                    </div>
                )}
            </div>
        </main>
    );
} 