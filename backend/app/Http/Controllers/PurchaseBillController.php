<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

use App\Models\PurchaseBill;

class PurchaseBillController extends Controller
{
    public function index()
    {
        $bills = PurchaseBill::with('supplier')->orderBy('issue_date', 'desc')->get();
        return response()->json(['data' => $bills]);
    }

    public function aiCreate(\Illuminate\Http\Request $request)
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
            
            // 1. Resolve Supplier
            $supplierId = null;
            if (!empty($validated['entity'])) {
                $entity = $validated['entity'];
                if (!empty($entity['id'])) {
                    $supplierId = $entity['id'];
                } else if (!empty($entity['name'])) {
                    // Create new supplier
                    $supplierId = \Illuminate\Support\Str::uuid()->toString();
                    \Illuminate\Support\Facades\DB::table('suppliers')->insert([
                        'id' => $supplierId,
                        'name' => $entity['name'],
                        'created_at' => $now,
                        'updated_at' => $now
                    ]);
                }
            }
            
            if (!$supplierId) {
                // Fallback to a default or anonymous supplier if missing
                $supplierId = \Illuminate\Support\Str::uuid()->toString();
                \Illuminate\Support\Facades\DB::table('suppliers')->insert([
                    'id' => $supplierId,
                    'name' => 'Cash Vendor',
                    'created_at' => $now,
                    'updated_at' => $now
                ]);
            }

            // 2. Create Purchase Bill
            $billId = \Illuminate\Support\Str::uuid()->toString();
            
            // Extract bill number if provided by AI, otherwise auto-generate
            $billNumber = 'BILL-' . strtoupper(\Illuminate\Support\Str::random(6));
            if (!empty($validated['operational_data']['invoice_number'])) {
                $billNumber = $validated['operational_data']['invoice_number'];
            }
            
            // Create a description from items
            $description = 'AI Generated Bill';
            if (!empty($validated['operational_data']['invoice_items'])) {
                $itemNames = array_map(function($item) {
                    return ($item['quantity'] ?? 1) . 'x ' . ($item['item_name'] ?? 'Item');
                }, $validated['operational_data']['invoice_items']);
                $description = implode(', ', $itemNames);
            }

            \Illuminate\Support\Facades\DB::table('purchase_bills')->insert([
                'id' => $billId,
                'supplier_id' => $supplierId,
                'bill_number' => $billNumber,
                'notes' => $description,
                'total_amount' => $validated['total_amount'],
                'status' => 'Open',
                'issue_date' => $now->toDateString(),
                'created_at' => $now,
                'updated_at' => $now
            ]);

            // 3. Create Journal Entry
            $journalEntryId = \Illuminate\Support\Str::uuid()->toString();
            \Illuminate\Support\Facades\DB::table('journal_entries')->insert([
                'id' => $journalEntryId,
                'entry_date' => $now->toDateString(),
                'narration' => 'Purchase Bill ' . $billNumber,
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
                'message' => 'Purchase Bill and Journal Entry created successfully',
                'bill_id' => $billId,
                'journal_entry_id' => $journalEntryId
            ], 201);
            
        } catch (\Exception $e) {
            \Illuminate\Support\Facades\DB::rollBack();
            return response()->json([
                'message' => 'Failed to process AI purchase bill',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}
