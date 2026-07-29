<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Invoice;

class InvoiceController extends Controller
{
    public function index()
    {
        return response()->json([
            'data' => Invoice::with('customer')->orderBy('created_at', 'desc')->get()
        ]);
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'customer_id' => 'required|exists:customers,id',
            'invoice_number' => 'required|string|unique:invoices,invoice_number',
            'description' => 'nullable|string',
            'total_amount' => 'required|numeric|min:0',
            'issue_date' => 'required|date',
            'due_date' => 'nullable|date'
        ]);

        $validated['status'] = 'Draft';

        $invoice = Invoice::create($validated);
        
        return response()->json([
            'message' => 'Invoice created successfully',
            'data' => $invoice
        ], 201);
    }

    public function aiCreate(Request $request)
    {
        $validated = $request->validate([
            'total_amount' => 'required|numeric|min:0',
            'line_items' => 'required|array',
            'operational_data' => 'nullable|array',
            'entity' => 'nullable|array',
        ]);

        try {
            \Illuminate\Support\Facades\DB::beginTransaction();
            $now = now();
            
            // 1. Resolve Customer
            $customerId = null;
            if (!empty($validated['entity'])) {
                $entity = $validated['entity'];
                if (!empty($entity['id'])) {
                    $customerId = $entity['id'];
                } else if (!empty($entity['name'])) {
                    // Create new customer
                    $customerId = \Illuminate\Support\Str::uuid()->toString();
                    \Illuminate\Support\Facades\DB::table('customers')->insert([
                        'id' => $customerId,
                        'name' => $entity['name'],
                        'created_at' => $now,
                        'updated_at' => $now
                    ]);
                }
            }
            
            if (!$customerId) {
                // Fallback to a default or anonymous customer if missing
                $customerId = \Illuminate\Support\Str::uuid()->toString();
                \Illuminate\Support\Facades\DB::table('customers')->insert([
                    'id' => $customerId,
                    'name' => 'Cash Customer',
                    'created_at' => $now,
                    'updated_at' => $now
                ]);
            }

            // 2. Create Invoice
            $invoiceId = \Illuminate\Support\Str::uuid()->toString();
            
            // Extract invoice number if provided by AI, otherwise auto-generate
            $invoiceNumber = 'INV-' . strtoupper(\Illuminate\Support\Str::random(6));
            if (!empty($validated['operational_data']['invoice_number'])) {
                $invoiceNumber = $validated['operational_data']['invoice_number'];
            }
            
            // Create a description from items
            $description = 'AI Generated Invoice';
            if (!empty($validated['operational_data']['invoice_items'])) {
                $itemNames = array_map(function($item) {
                    return ($item['quantity'] ?? 1) . 'x ' . ($item['item_name'] ?? 'Item');
                }, $validated['operational_data']['invoice_items']);
                $description = implode(', ', $itemNames);
            }

            \Illuminate\Support\Facades\DB::table('invoices')->insert([
                'id' => $invoiceId,
                'customer_id' => $customerId,
                'invoice_number' => $invoiceNumber,
                'description' => $description,
                'total_amount' => $validated['total_amount'],
                'status' => 'Sent',
                'issue_date' => $now->toDateString(),
                'created_at' => $now,
                'updated_at' => $now
            ]);

            // 3. Create Journal Entry
            $journalEntryId = \Illuminate\Support\Str::uuid()->toString();
            \Illuminate\Support\Facades\DB::table('journal_entries')->insert([
                'id' => $journalEntryId,
                'entry_date' => $now->toDateString(),
                'narration' => 'Sales Invoice ' . $invoiceNumber,
                'status' => 'Posted',
                'created_at' => $now,
                'updated_at' => $now,
            ]);

            foreach ($validated['line_items'] as $line) {
                $accountId = $line['account_id'];
                if (!$accountId) {
                    $fallback = \Illuminate\Support\Facades\DB::table('accounts')->first();
                    $accountId = $fallback->id ?? \Illuminate\Support\Str::uuid()->toString();
                }

                \Illuminate\Support\Facades\DB::table('journal_lines')->insert([
                    'id' => \Illuminate\Support\Str::uuid()->toString(),
                    'journal_entry_id' => $journalEntryId,
                    'account_id' => $accountId,
                    'debit_amount' => $line['dc'] === 'debit' ? $line['amount'] : 0,
                    'credit_amount' => $line['dc'] === 'credit' ? $line['amount'] : 0,
                    'created_at' => $now,
                    'updated_at' => $now,
                ]);
            }

            \Illuminate\Support\Facades\DB::commit();

            return response()->json([
                'message' => 'Invoice and Journal Entry created successfully',
                'invoice_id' => $invoiceId,
                'journal_entry_id' => $journalEntryId
            ], 201);
            
        } catch (\Exception $e) {
            \Illuminate\Support\Facades\DB::rollBack();
            return response()->json([
                'message' => 'Failed to process AI invoice',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}
