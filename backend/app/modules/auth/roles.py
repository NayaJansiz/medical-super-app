from enum import StrEnum


class Role(StrEnum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    CLINIC_ADMIN = "clinic_admin"
    PHARMACIST = "pharmacist"
    STUDENT = "student"
    LAB_STAFF = "lab_staff"
    SUPER_ADMIN = "super_admin"


ALL_ROLES = [role.value for role in Role]
