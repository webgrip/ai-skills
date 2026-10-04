const money = new Intl.NumberFormat(navigator.language, { style: "currency", currency: "EUR" });
const day = new Intl.DateTimeFormat(navigator.language, { dateStyle: "medium" });
const plural = new Intl.PluralRules(navigator.language);
const invoiceWord = { one: "invoice", other: "invoices" };

export function describeSelection(count) {
  return `${count} ${invoiceWord[plural.select(count)] ?? invoiceWord.other} selected`;
}

export function archiveInvoices(invoices, toastRegion) {
  hide(invoices);
  toastRegion.textContent = `Archived ${describeSelection(invoices.length)}.`;
  return { undo: () => show(invoices), total: money.format(sum(invoices)), due: day.format(invoices[0].due) };
}

export function explainFailure(response) {
  return response.status === 409
    ? "Someone else changed this invoice while you were editing. Reload to see their version; your text is kept below."
    : "We could not reach the server, so nothing was saved. Check your connection and try again.";
}
