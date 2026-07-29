<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Concerns\HasUuids;

class PurchasePayment extends Model
{
    use HasFactory, HasUuids;
    public $timestamps = false;
    protected $guarded = [];

    public function bill() {
        return $this->belongsTo(PurchaseBill::class, 'purchase_bill_id');
    }
}
