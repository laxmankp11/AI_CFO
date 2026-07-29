<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Concerns\HasUuids;

class Supplier extends Model
{
    use HasUuids;

    protected $fillable = [
        'name',
        'gstin',
        'contact_person',
        'default_expense_category'
    ];
}
