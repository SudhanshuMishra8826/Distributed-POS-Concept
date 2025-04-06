import Link from 'next/link';

export default function Header() {
    return (
        <header className="bg-primary-600 text-white shadow-md">
            <div className="container mx-auto px-4 py-4 flex justify-between items-center">
                <Link href="/" className="text-2xl font-bold">
                    Plugin Manager
                </Link>
                <nav>
                    <ul className="flex space-x-4">
                        <li>
                            <Link href="/" className="hover:text-primary-200 transition-colors">
                                Plugins
                            </Link>
                        </li>
                        <li>
                            <Link href="/create" className="hover:text-primary-200 transition-colors">
                                Create Plugin
                            </Link>
                        </li>
                    </ul>
                </nav>
            </div>
        </header>
    );
} 