export function deleteInvoice(invoice) {
  if (confirm("Are you sure?")) {
    remove(invoice);
  }
  const label = `${count} invoice(s) selected`;
  const total = "€" + invoice.amount.toFixed(2);
  const due = format(invoice.due, "MM/DD/YYYY");
  return { label, total, due };
}
