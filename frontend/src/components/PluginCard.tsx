import { Plugin } from '@/types/plugin';
import Link from 'next/link';
import { FaEdit, FaTrash, FaToggleOn, FaToggleOff } from 'react-icons/fa';

interface PluginCardProps {
    plugin: Plugin;
    onDelete: (id: string) => void;
    onToggleStatus: (id: string, active: boolean) => void;
}

export default function PluginCard({ plugin, onDelete, onToggleStatus }: PluginCardProps) {
    const handleDelete = () => {
        if (window.confirm(`Are you sure you want to delete the plugin "${plugin.id}"?`)) {
            onDelete(plugin.id);
        }
    };

    const handleToggleStatus = () => {
        onToggleStatus(plugin.id, !plugin.active);
    };

    return (
        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="flex justify-between items-start mb-4">
                <h2 className="text-xl font-semibold text-gray-800">{plugin.id}</h2>
                <div className="flex space-x-2">
                    <button
                        onClick={handleToggleStatus}
                        className={`p-2 rounded-full ${plugin.active ? 'text-green-500 hover:text-green-600' : 'text-gray-400 hover:text-gray-500'
                            }`}
                        title={plugin.active ? 'Deactivate Plugin' : 'Activate Plugin'}
                    >
                        {plugin.active ? <FaToggleOn size={20} /> : <FaToggleOff size={20} />}
                    </button>
                    <Link
                        href={`/edit/${plugin.id}`}
                        className="p-2 text-blue-500 hover:text-blue-600 rounded-full"
                        title="Edit Plugin"
                    >
                        <FaEdit size={20} />
                    </Link>
                    <button
                        onClick={handleDelete}
                        className="p-2 text-red-500 hover:text-red-600 rounded-full"
                        title="Delete Plugin"
                    >
                        <FaTrash size={20} />
                    </button>
                </div>
            </div>

            <div className="mb-4">
                <span className={`inline-block px-2 py-1 text-xs font-semibold rounded-full ${plugin.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                    {plugin.active ? 'Active' : 'Inactive'}
                </span>
            </div>

            <div className="space-y-2">
                <div>
                    <h3 className="text-sm font-medium text-gray-500">Filters</h3>
                    <pre className="mt-1 text-sm bg-black p-2 rounded overflow-auto max-h-24">
                        {plugin.filters ? JSON.stringify(plugin.filters, null, 2) : 'No filters'}
                    </pre>
                </div>

                <div>
                    <h3 className="text-sm font-medium text-gray-500">Actions</h3>
                    <pre className="mt-1 text-sm bg-black p-2 rounded overflow-auto max-h-24">
                        {plugin.actions ? JSON.stringify(plugin.actions, null, 2) : 'No actions'}
                    </pre>
                </div>
            </div>
        </div>
    );
} 