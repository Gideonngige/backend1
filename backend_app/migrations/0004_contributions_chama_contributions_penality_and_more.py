# Generated by Django 5.1.6 on 2025-02-27 21:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_app', '0003_remove_loans_member_loans_approved_by_loans_chama_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='contributions',
            name='chama',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='backend_app.chamas'),
        ),
        migrations.AddField(
            model_name='contributions',
            name='penality',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.CreateModel(
            name='LoanRepayment',
            fields=[
                ('repayment_id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('penality', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('loan_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend_app.loans')),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend_app.members')),
            ],
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('transaction_id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_type', models.CharField(choices=[('Contribution', 'Contribution'), ('Loan repayment', 'Loan repayment'), ('Loan', 'Loan'), ('Expense', 'Expense'), ('Other', 'Other')], default='Other', max_length=20)),
                ('transaction_date', models.DateTimeField(auto_now_add=True)),
                ('chama', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend_app.chamas')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend_app.members')),
            ],
        ),
    ]
