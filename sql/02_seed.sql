-- Idempotent insert-only fictional seed. Never overwrites an existing event.
MERGE INTO CF_DEMO.RAW.PROJECTS t
USING (SELECT column1 AS PROJECT_ID, column2 AS PROJECT_NAME, column3 AS LOCATION, column4 AS LOAN_PRINCIPAL, column5 AS ANNUAL_INTEREST_RATE FROM VALUES
('P001', '湾岸冷凍倉庫用地（架空）', '架空地域', 70000000, 0.03),
('P002', '北部物流用地（架空）', '架空地域', 100000000, 0.03),
('P003', '西部自動倉庫用地（架空）', '架空地域', 60000000, 0.03)
) s ON t.PROJECT_ID=s.PROJECT_ID
WHEN NOT MATCHED THEN INSERT (PROJECT_ID, PROJECT_NAME, LOCATION, LOAN_PRINCIPAL, ANNUAL_INTEREST_RATE) VALUES (s.PROJECT_ID, s.PROJECT_NAME, s.LOCATION, s.LOAN_PRINCIPAL, s.ANNUAL_INTEREST_RATE);

MERGE INTO CF_DEMO.RAW.CASH_EVENTS t
USING (SELECT column1 AS EVENT_ID, column2 AS PROJECT_ID, column3 AS COUNTERPARTY, column4 AS CATEGORY, column5 AS PLANNED_DATE, column6 AS PLANNED_AMOUNT, column7 AS ACTUAL_DATE, column8 AS ACTUAL_AMOUNT FROM VALUES
('P001-draw', 'P001', '架空金融機関', 'loan_draw', '2026-10-15', 70000000, '2026-10-15', 70000000),
('P001-land', 'P001', '架空土地所有者', 'land_purchase', '2026-10-15', -100000000, '2026-10-15', -100000000),
('P001-survey', 'P001', '架空調査設計会社', 'survey', '2026-11-15', -2000000, NULL, NULL),
('P001-tax', 'P001', '架空税費用先', 'tax_fee', '2026-12-15', -3000000, NULL, NULL),
('P001-interest-1', 'P001', '架空金融機関', 'interest', '2026-11-15', -175000, NULL, NULL),
('P001-interest-2', 'P001', '架空金融機関', 'interest', '2026-12-15', -175000, NULL, NULL),
('P001-interest-3', 'P001', '架空金融機関', 'interest', '2027-01-15', -175000, NULL, NULL),
('P001-interest-4', 'P001', '架空金融機関', 'interest', '2027-02-15', -175000, NULL, NULL),
('P001-interest-5', 'P001', '架空金融機関', 'interest', '2027-03-15', -175000, NULL, NULL),
('P001-interest-6', 'P001', '架空金融機関', 'interest', '2027-04-15', -175000, NULL, NULL),
('P001-sale', 'P001', '架空開発ファンド', 'land_sale', '2027-04-15', 128000000, NULL, NULL),
('P001-repay', 'P001', '架空金融機関', 'principal_repayment', '2027-04-15', -70000000, NULL, NULL),
('P001-fee-7', 'P001', '架空開発ファンド', 'management_fee', '2027-05-15', 500000, NULL, NULL),
('P001-fee-8', 'P001', '架空開発ファンド', 'management_fee', '2027-06-15', 500000, NULL, NULL),
('P001-fee-9', 'P001', '架空開発ファンド', 'management_fee', '2027-07-15', 500000, NULL, NULL),
('P001-fee-10', 'P001', '架空開発ファンド', 'management_fee', '2027-08-15', 500000, NULL, NULL),
('P001-fee-11', 'P001', '架空開発ファンド', 'management_fee', '2027-09-15', 500000, NULL, NULL),
('P001-fee-12', 'P001', '架空開発ファンド', 'management_fee', '2027-10-15', 500000, NULL, NULL),
('P002-draw', 'P002', '架空金融機関', 'loan_draw', '2027-01-15', 100000000, NULL, NULL),
('P002-land', 'P002', '架空土地所有者', 'land_purchase', '2027-01-15', -150000000, NULL, NULL),
('P002-survey', 'P002', '架空調査設計会社', 'survey', '2027-02-15', -2000000, NULL, NULL),
('P002-tax', 'P002', '架空税費用先', 'tax_fee', '2027-03-15', -3000000, NULL, NULL),
('P002-interest-1', 'P002', '架空金融機関', 'interest', '2027-02-15', -250000, NULL, NULL),
('P002-interest-2', 'P002', '架空金融機関', 'interest', '2027-03-15', -250000, NULL, NULL),
('P002-interest-3', 'P002', '架空金融機関', 'interest', '2027-04-15', -250000, NULL, NULL),
('P002-interest-4', 'P002', '架空金融機関', 'interest', '2027-05-15', -250000, NULL, NULL),
('P002-interest-5', 'P002', '架空金融機関', 'interest', '2027-06-15', -250000, NULL, NULL),
('P002-interest-6', 'P002', '架空金融機関', 'interest', '2027-07-15', -250000, NULL, NULL),
('P002-sale', 'P002', '架空開発ファンド', 'land_sale', '2027-07-15', 188000000, NULL, NULL),
('P002-repay', 'P002', '架空金融機関', 'principal_repayment', '2027-07-15', -100000000, NULL, NULL),
('P002-fee-7', 'P002', '架空開発ファンド', 'management_fee', '2027-08-15', 500000, NULL, NULL),
('P002-fee-8', 'P002', '架空開発ファンド', 'management_fee', '2027-09-15', 500000, NULL, NULL),
('P002-fee-9', 'P002', '架空開発ファンド', 'management_fee', '2027-10-15', 500000, NULL, NULL),
('P002-fee-10', 'P002', '架空開発ファンド', 'management_fee', '2027-11-15', 500000, NULL, NULL),
('P002-fee-11', 'P002', '架空開発ファンド', 'management_fee', '2027-12-15', 500000, NULL, NULL),
('P002-fee-12', 'P002', '架空開発ファンド', 'management_fee', '2028-01-15', 500000, NULL, NULL),
('P003-draw', 'P003', '架空金融機関', 'loan_draw', '2027-06-15', 60000000, NULL, NULL),
('P003-land', 'P003', '架空土地所有者', 'land_purchase', '2027-06-15', -90000000, NULL, NULL),
('P003-survey', 'P003', '架空調査設計会社', 'survey', '2027-07-15', -2000000, NULL, NULL),
('P003-tax', 'P003', '架空税費用先', 'tax_fee', '2027-08-15', -3000000, NULL, NULL),
('P003-interest-1', 'P003', '架空金融機関', 'interest', '2027-07-15', -150000, NULL, NULL),
('P003-interest-2', 'P003', '架空金融機関', 'interest', '2027-08-15', -150000, NULL, NULL),
('P003-interest-3', 'P003', '架空金融機関', 'interest', '2027-09-15', -150000, NULL, NULL),
('P003-interest-4', 'P003', '架空金融機関', 'interest', '2027-10-15', -150000, NULL, NULL),
('P003-interest-5', 'P003', '架空金融機関', 'interest', '2027-11-15', -150000, NULL, NULL),
('P003-interest-6', 'P003', '架空金融機関', 'interest', '2027-12-15', -150000, NULL, NULL),
('P003-sale', 'P003', '架空開発ファンド', 'land_sale', '2027-12-15', 115000000, NULL, NULL),
('P003-repay', 'P003', '架空金融機関', 'principal_repayment', '2027-12-15', -60000000, NULL, NULL),
('P003-fee-7', 'P003', '架空開発ファンド', 'management_fee', '2028-01-15', 500000, NULL, NULL),
('P003-fee-8', 'P003', '架空開発ファンド', 'management_fee', '2028-02-15', 500000, NULL, NULL),
('P003-fee-9', 'P003', '架空開発ファンド', 'management_fee', '2028-03-15', 500000, NULL, NULL),
('P003-fee-10', 'P003', '架空開発ファンド', 'management_fee', '2028-04-15', 500000, NULL, NULL),
('P003-fee-11', 'P003', '架空開発ファンド', 'management_fee', '2028-05-15', 500000, NULL, NULL),
('P003-fee-12', 'P003', '架空開発ファンド', 'management_fee', '2028-06-15', 500000, NULL, NULL)
) s ON t.EVENT_ID=s.EVENT_ID
WHEN NOT MATCHED THEN INSERT (EVENT_ID, PROJECT_ID, COUNTERPARTY, CATEGORY, PLANNED_DATE, PLANNED_AMOUNT, ACTUAL_DATE, ACTUAL_AMOUNT) VALUES (s.EVENT_ID, s.PROJECT_ID, s.COUNTERPARTY, s.CATEGORY, s.PLANNED_DATE, s.PLANNED_AMOUNT, s.ACTUAL_DATE, s.ACTUAL_AMOUNT);

