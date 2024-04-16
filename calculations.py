DeductionsOld = {
    '80C': 150000,  # Includes EPF, PPF, NSC, ELSS, etc.
    '80CCC': 150000,  # Pension funds
    '80CCD(1)': 150000,  # NPS, APY contribution limits
    '80CCD(1B)': 50000,  # Additional NPS
    '80CCD(2)': '10% of salary',  # Employer's NPS (special handling required)
    '80D': {'self': 25000, 'parents': 50000},  # Medical insurance
    '80DD': {'normal': 75000, 'severe': 125000},  # Dependent disability
    '80DDB': {'<60': 40000, '>60': 100000},  # Specified diseases
    '80E': 'actual interest paid',  # Education loan interest
    '80EE': 50000,  # First-time homeowners
    '80EEA': 150000,  # Home loan interest under certain conditions
    '80EEB': 150000,  # Electric vehicles
    '80G': 'depends on donee',  # Donations
    '80GG': 'least of specific calculations',  # Rent paid
    '80GGA': '100% of donation',  # Scientific research or rural development
    '80GGC': 'amount contributed',  # Political contributions
    '80RRB': 300000,  # Royalties on patents
    '80TTA': 10000,  # Interest on savings
    '80TTB': 50000,  # Senior citizens' interest
    '80U': {'normal': 75000, 'severe': 125000},  # Disability
    '24B': 200000,  # Home loan interest
    '10(13A)': 'HRA Calculation',  # HRA
    '10(5)': 'LTA Calculation',  # LTA
}

# New Tax Regime Deductions
DeductionsNew = {
    'standard': 50000,  #Standard deduction
}




class Calculations:
    def old(self, income):
        slabs = [
            (250000, 0.0), (300000, 0.0), (500000, 0.0),
            (600000, 0.0), (900000, 0.0), (1000000, 0.0),
            (1200000, 0.0), (1500000, 0.0)
        ]
        tax = 0
        for slab, rate in slabs:
            if income > slab:
                nextSlab = next((s for s, _ in slabs if s > slab), float('inf'))
                taxable = min(income-slab, nextSlab - slab)
                tax += taxable * rate
            else:
                break
        return tax
    
    def new(self, income):
        slabs = [
            (250000, 0.0), (300000, 0.0), (500000, 0.05),
            (600000, 0.05), (900000, 0.10), (1000000, 0.15),
            (1200000, 0.15), (1500000, 0.20)
        ]
        tax = 0
        for slab, rate in slabs:
            if income > slab:
                nextSlab = next((s for s, _ in slabs if s > slab), float('inf'))
                taxable = min(income-slab, nextSlab - slab)
                tax += taxable * rate
            else:
                break
        return tax
    
    def calcHRA(self, hra, basicSalary, rentPaid, city):
        percentage = 0.5 if city.lower() == 'metro' else 0.4
        cond1 = hra
        cond2 = basicSalary * percentage
        cond3 = rentPaid - (basicSalary * 0.10)

        hraExempt = min(cond1, cond2, cond3)
        return hraExempt
    
    def calcDeductions(self, income, deductions, limits):
        total = 0
        group80C = 150000

        group80Cdeductions = sum(min(deductions.get(sec, 0), limits.get(sec, 0)) for sec in ['80C', '80CCC', '80CCD(1)', '80CCD(1B)', '80CCD(2)'])
        group80Cdeductions = min(group80Cdeductions, group80C)

        total += group80Cdeductions

        for key, limit in limits.items():
            if key not in ['80C', '80CCC', '80CCD(1)', '80CCD(1B)', '80CCD(2)']:
                if isinstance(limit, int):
                    total += min(deductions.get(key, 0), limit)
                elif key == '80D':
                    total += min(deductions.get('self', 0), limit['self'])
                    total += min(deductions.get('parents', 0), limit['parents'])
                elif key == '80U':
                    total += min(deductions.get('normal', 0), limit['normal'])
                    total += min(deductions.get('severe', 0), limit['severe'])
        
        return max(0, income-total)
    
    def compareRegime(self, income, deductions, old=DeductionsOld, new=DeductionsNew):
        totalOld = sum(min(deductions.get(key, 0), limit) if isinstance(limit, int) else 0 for key, limit in old.items())
        taxableOld = max(0, income-totalOld)
        taxDueOld = self.old(taxableOld)

        taxableNew = max(0, income - new['standard'])
        taxDueNew = self.new(taxableNew)

        if taxDueOld < taxDueNew:
            result = f"The Old tax regime is more beneficial. Old regime tax: {taxDueOld}, New regime tax: {taxDueNew}"
        else:
            result = f"The New tax regime is more beneficial. Old regime tax: {taxDueOld}, New regime tax: {taxDueNew}"

        return result