'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import Header from '@/components/Header';
import PluginForm from '@/components/PluginForm';
import { Plugin, PluginUpdate } from '@/types/plugin';
import { getPlugin, updatePlugin } from '@/lib/api';

interface EditPluginProps {
    params: {
        id: string;
    };
}

export default function EditPlugin({ params }: EditPluginProps) {
    const [plugin, setPlugin] = useState<Plugin | null>(null);
    const [loading, setLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const router = useRouter();
    const { id } = params;

    useEffect(() => {
        fetchPlugin();
    }, [id]);

    const fetchPlugin = async () => {
        try {
            setLoading(true);
            const data = await getPlugin(id);
            setPlugin(data);
        } catch (error) {
            toast.error('Failed to fetch plugin');
            console.error(error);
            router.push('/');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (data: PluginUpdate) => {
        try {
            setIsSubmitting(true);
            await updatePlugin(id, data);
            toast.success('Plugin updated successfully');
            router.push('/');
        } catch (error) {
            toast.error('Failed to update plugin');
            console.error(error);
        } finally {
            setIsSubmitting(false);
        }
    };

    if (loading) {
        return (
            <main className="min-h-screen bg-gray-50">
                <Header />
                <div className="container mx-auto px-4 py-8">
                    <div className="flex justify-center items-center h-64">
                        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
                    </div>
                </div>
            </main>
        );
    }

    if (!plugin) {
        return null;
    }

    return (
        <main className="min-h-screen bg-gray-50">
            <Header />

            <div className="container mx-auto px-4 py-8">
                <div className="max-w-2xl mx-auto">
                    <div className="mb-6">
                        <h1 className="text-2xl font-bold text-gray-800">Edit Plugin: {plugin.id}</h1>
                        <p className="mt-1 text-sm text-gray-500">
                            Update the plugin details below.
                        </p>
                    </div>

                    <div className="bg-white shadow rounded-lg p-6">
                        <PluginForm
                            initialData={plugin}
                            onSubmit={handleSubmit}
                            isEdit={true}
                        />
                    </div>

                    <div className="mt-6 flex justify-end">
                        <button
                            onClick={() => router.push('/')}
                            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        </main>
    );
} 