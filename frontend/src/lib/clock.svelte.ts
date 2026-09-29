// One shared one-second tick for all countdowns on a page.

export const clock = $state({ now: Date.now() });

let timer: ReturnType<typeof setInterval> | undefined;
let users = 0;

/** Start ticking; returns a stop function (for onMount cleanup). */
export function useClock(): () => void {
	users++;
	if (!timer) {
		clock.now = Date.now();
		timer = setInterval(() => (clock.now = Date.now()), 1000);
	}
	return () => {
		users--;
		if (users === 0 && timer) {
			clearInterval(timer);
			timer = undefined;
		}
	};
}
