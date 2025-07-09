from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from datetime import date, datetime

# ------------------ Submodels ------------------

class PersonalInfo(BaseModel):
    firstName: str
    middleName: Optional[str]
    lastName: str
    suffix: Optional[str]
    dob: date
    ssn: str
    gender: str
    maritalStatus: str
    citizenship: str

class ContactInfo(BaseModel):
    email: str
    phoneMobile: str
    phoneHome: Optional[str]
    phoneWork: Optional[str]
    preferredContactMethod: Optional[str]

class Address(BaseModel):
    street: str
    city: str
    state: str
    zipCode: str
    country: str
    residenceType: Optional[str]
    sinceDate: Optional[date]

class EmploymentInfo(BaseModel):
    employmentStatus: str
    employerName: str
    jobTitle: str
    startDate: date
    endDate: Optional[date]
    annualIncome: float
    payFrequency: str

class Financials(BaseModel):
    totalAssets: float
    totalLiabilities: float
    netWorth: float
    monthlyDebtObligations: float

class CreditInfo(BaseModel):
    creditScore: int
    bureau: str
    creditHistoryLengthYears: int
    numOpenAccounts: int
    numDerogatoryMarks: int

class KycInfo(BaseModel):
    idType: str
    idNumber: str
    idIssueDate: date
    idExpiryDate: date

class Disclosures(BaseModel):
    isPoliticallyExposed: bool
    hasBankruptcyHistory: bool
    hasCriminalRecord: bool
    agreedToTerms: bool

class Applicant(BaseModel):
    applicantId: str
    role: str
    personalInfo: PersonalInfo
    contactInfo: ContactInfo
    currentAddress: Address
    previousAddress: Optional[Address]
    employmentInfo: EmploymentInfo
    financials: Financials
    creditInfo: CreditInfo
    kycInfo: KycInfo
    disclosures: Disclosures

class CoApplicant(BaseModel):
    applicantId: str
    role: str
    personalInfo: PersonalInfo
    contactInfo: ContactInfo
    relationshipToPrimary: Optional[str]
    annualIncome: Optional[float]

class PropertyAddress(BaseModel):
    street: str
    city: str
    state: str
    zipCode: str
    country: str

class PropertyInfo(BaseModel):
    propertyType: str
    address: PropertyAddress
    estimatedValue: float
    purchasePrice: float
    yearBuilt: int
    propertyUsage: str

class Asset(BaseModel):
    type: str
    description: str
    value: float
    ownerApplicantId: str

class Liability(BaseModel):
    type: str
    description: str
    outstandingAmount: float
    monthlyPayment: float
    ownerApplicantId: str

class Collateral(BaseModel):
    collateralType: str
    estimatedValue: float
    ownership: str

class Fees(BaseModel):
    originationFee: float
    processingFee: float
    insuranceFee: float
    totalFees: float

class Underwriting(BaseModel):
    decision: str
    approvedAmount: float
    approvedTenureMonths: int
    approvalDate: date
    conditions: Optional[str]

class DocumentChecklistItem(BaseModel):
    documentType: str
    provided: bool
    verified: bool

class DisclosureFlags(BaseModel):
    electronicConsent: bool
    privacyPolicyAcknowledged: bool
    termsAndConditionsAccepted: bool

class Metadata(BaseModel):
    createdBy: str
    createdTimestamp: datetime
    lastModifiedBy: str
    lastModifiedTimestamp: datetime

# ------------------ Main model ------------------

class LoanApplication(BaseModel):
    applicationId: str
    applicationDate: date
    productType: str
    loanAmount: float
    loanPurpose: str
    tenureMonths: int
    interestRate: float
    repaymentType: str
    channel: str
    branchCode: str
    originatorId: str
    promoCode: Optional[str]
    applicants: List[Applicant]
    coApplicants: Optional[List[CoApplicant]]
    propertyInfo: PropertyInfo
    assets: Optional[List[Asset]]
    liabilities: Optional[List[Liability]]
    collateral: Optional[Collateral]
    fees: Optional[Fees]
    underwriting: Optional[Underwriting]
    documentChecklist: Optional[List[DocumentChecklistItem]]
    disclosures: DisclosureFlags
    metadata: Metadata

    @model_validator(mode="after")
    def check_loan_vs_property(cls, values):
        prop = values.propertyInfo
        loan = values.loanAmount
        if prop and loan and loan > prop.estimatedValue:
            raise ValueError("loanAmount must not exceed property estimatedValue")
        return values
