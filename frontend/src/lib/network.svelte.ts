// Online state: browser events plus the outcome of the last API request.

export const network = $state({ online: true });

export function markOffline() {
	network.online = false;
}

export function markOnline() {
	network.online = true;
}

export function watchNetwork(): () => void {
	network.online = navigator.onLine;
	const on = () => markOnline();
	const off = () => markOffline();
	window.addEventListener('online', on);
	window.addEventListener('offline', off);
	return () => {
		window.removeEventListener('online', on);
		window.removeEventListener('offline', off);
	};
}
