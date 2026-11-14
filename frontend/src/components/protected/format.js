export const money = (value) => `KES ${Number(value).toLocaleString('en-KE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
export const dateTime = (value) => value ? new Date(value).toLocaleString('en-KE', { timeZone: 'Africa/Nairobi' }) + ' EAT' : 'Not set'
