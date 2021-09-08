from .eagle_eye_api import EagleEyeApi


class EagleEyeResources(EagleEyeApi):
    def list_campaigns(self, limit=100, offset=0):
        return self.get(f"/campaigns", query=dict(limit=limit, offset=offset))

    def create_campaign(self, data):
        return self.post(f"/campaigns", data=data)

    def get_campaign(self, campaign_id):
        return self.get(f"/campaigns/{campaign_id}")

    def update_campaign(self, campaign_id, data):
        return self.post(f"/campaigns/{campaign_id}", data=data)

    def delete_campaign(self, campaign_id):
        return self.delete(f"/campaigns/{campaign_id}")

    def get_campaign_reference(self, reference):
        return self.get(f"/campaigns/reference/{reference}")

    def set_campaign_reference(self, reference, data):
        return self.put(f"/campaigns/reference/{reference}", data=data)

    def delete_campaign_reference(self, reference):
        return self.delete(f"/campaigns/reference/{reference}")

    def validate_campaign(self, data):
        return self.post(f"/campaigns/validate", data=data)

    def list_schemes(self):
        return self.get(f"/schemes/points")
