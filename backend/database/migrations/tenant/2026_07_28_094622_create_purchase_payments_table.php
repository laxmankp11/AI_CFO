<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('purchase_payments', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->uuid('purchase_bill_id');
            $table->date('payment_date');
            $table->decimal('amount', 15, 2);
            $table->string('payment_method');
            $table->string('reference_number')->nullable();
            
            $table->foreign('purchase_bill_id')->references('id')->on('purchase_bills');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('purchase_payments');
    }
};
