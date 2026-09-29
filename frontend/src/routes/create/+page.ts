import { guard } from '$lib/guard';
import type { PageLoad } from './$types';

export const load: PageLoad = ({ fetch }) => guard('no-character', fetch);
