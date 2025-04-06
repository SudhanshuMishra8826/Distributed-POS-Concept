'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import Header from '@/components/Header';
import PluginForm from '@/components/PluginForm';
import { Plugin } from '@/types/plugin';
import { createPlugin } from '@/lib/api';

export default function CreatePlugin() {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const router = useRouter();

    const handleSubmit = async (data: Plugin) => {
        try {
            setIsSubmitting(true);
            await createPlugin(data);
            toast.success('Plugin created successfully');
            router.push('/');
        } catch (error) {
            toast.error('Failed to create plugin');
            console.error(error);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <main className="min-h-screen bg-gray-50">
            <Header />

            <div className="container mx-auto px-4 py-8">
                <div className="max-w-2xl mx-auto">
                    <div className="mb-6">
                        <h1 className="text-2xl font-bold text-gray-800">Create New Plugin</h1>
                        <p className="mt-1 text-sm text-gray-500">
                            Fill in the details to create a new plugin.
                        </p>
                    </div>

                    <div className="bg-white shadow rounded-lg p-6">
                        <PluginForm onSubmit={handleSubmit} />
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