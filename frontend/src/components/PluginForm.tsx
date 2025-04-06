import { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { Plugin, PluginUpdate } from '@/types/plugin';

interface PluginFormProps {
    initialData?: Partial<Plugin>;
    onSubmit: (data: Plugin | PluginUpdate) => void;
    isEdit?: boolean;
}

export default function PluginForm({ initialData, onSubmit, isEdit = false }: PluginFormProps) {
    const [filtersError, setFiltersError] = useState<string | null>(null);
    const [actionsError, setActionsError] = useState<string | null>(null);

    const { register, handleSubmit, control, formState: { errors } } = useForm<Plugin>({
        defaultValues: {
            id: initialData?.id || '',
            active: initialData?.active ?? true,
            filters: initialData?.filters || null,
            actions: initialData?.actions || null,
        },
    });

    const handleFormSubmit = (data: Plugin) => {
        // Validate JSON fields
        try {
            if (data.filters && typeof data.filters === 'string') {
                data.filters = JSON.parse(data.filters);
            }
            setFiltersError(null);
        } catch (e) {
            setFiltersError('Invalid JSON format for filters');
            return;
        }

        try {
            if (data.actions && typeof data.actions === 'string') {
                data.actions = JSON.parse(data.actions);
            }
            setActionsError(null);
        } catch (e) {
            setActionsError('Invalid JSON format for actions');
            return;
        }

        onSubmit(data);
    };

    return (
        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
            <div>
                <label htmlFor="id" className="block text-sm font-medium text-gray-700">
                    Plugin ID
                </label>
                <input
                    type="text"
                    id="id"
                    {...register('id', { required: !isEdit })}
                    disabled={isEdit}
                    className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm ${isEdit ? 'bg-gray-100' : ''
                        }`}
                />
                {errors.id && <p className="mt-1 text-sm text-red-600">{errors.id.message}</p>}
            </div>

            <div className="flex items-center">
                <input
                    type="checkbox"
                    id="active"
                    {...register('active')}
                    className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <label htmlFor="active" className="ml-2 block text-sm text-gray-700">
                    Active
                </label>
            </div>

            <div>
                <label htmlFor="filters" className="block text-sm font-medium text-gray-700">
                    Filters (JSON)
                </label>
                <Controller
                    name="filters"
                    control={control}
                    render={({ field }) => (
                        <textarea
                            id="filters"
                            {...field}
                            rows={4}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm font-mono"
                            placeholder='{"type": "payment"}'
                            value={typeof field.value === 'object' ? JSON.stringify(field.value, null, 2) : field.value || ''}
                            onChange={(e) => field.onChange(e.target.value)}
                        />
                    )}
                />
                {filtersError && <p className="mt-1 text-sm text-red-600">{filtersError}</p>}
            </div>

            <div>
                <label htmlFor="actions" className="block text-sm font-medium text-gray-700">
                    Actions (JSON)
                </label>
                <Controller
                    name="actions"
                    control={control}
                    render={({ field }) => (
                        <textarea
                            id="actions"
                            {...field}
                            rows={4}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm font-mono"
                            placeholder='{"type": "process_payment"}'
                            value={typeof field.value === 'object' ? JSON.stringify(field.value, null, 2) : field.value || ''}
                            onChange={(e) => field.onChange(e.target.value)}
                        />
                    )}
                />
                {actionsError && <p className="mt-1 text-sm text-red-600">{actionsError}</p>}
            </div>

            <div className="flex justify-end">
                <button
                    type="submit"
                    className="inline-flex justify-center rounded-md border border-transparent bg-primary-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
                >
                    {isEdit ? 'Update Plugin' : 'Create Plugin'}
                </button>
            </div>
        </form>
    );
} 