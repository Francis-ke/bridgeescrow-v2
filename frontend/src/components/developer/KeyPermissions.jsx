export const permissions = ['escrow:read', 'escrow:write', 'checkout:write', 'dispute:write', 'release:request']
export default function KeyPermissions({ value, onChange }) {
  return <fieldset><legend className="mb-2 text-xs text-slate-400">Application permissions</legend>
    <div className="grid gap-2 sm:grid-cols-2">{permissions.map((item) => <label key={item} className="flex items-center gap-2 text-xs text-slate-300">
      <input type="checkbox" checked={value.includes(item)} onChange={(event) => onChange(event.target.checked ? [...value, item] : value.filter((entry) => entry !== item))}
        className="accent-teal-400" />{item}
    </label>)}</div>
  </fieldset>
}
