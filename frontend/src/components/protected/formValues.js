export function localDate(hours) {
  const date = new Date(Date.now() + hours * 3600000)
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16)
}
export const initialForm = () => ({ title: '', description: '', amount: '', provider_id: '',
  deadline: localDate(168), booking_start: localDate(48), booking_end: localDate(49) })
export function createPayload(category, form, rules, milestones) {
  const date = (value) => new Date(value).toISOString()
  return { category, title: form.title, description: form.description, amount: form.amount,
    provider_id: Number(form.provider_id), deadline: date(form.deadline),
    booking_start: category === 'booking' ? date(form.booking_start) : null,
    booking_end: category === 'booking' ? date(form.booking_end) : null,
    rules: { ...rules, cancellation_deadline: date(rules.cancellation_deadline) },
    milestones: milestones.map((m) => ({ ...m, deadline: date(m.deadline) })) }
}
