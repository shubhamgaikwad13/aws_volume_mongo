class Volume:

    def __init__(self, id, zone, create_time, is_encrypted, size, snapshot_id, state, iops, volume_type, multi_attach_enabled, is_active):
        self.volume_id = id
        self.zone = zone
        self.create_time = create_time
        self.is_encrypted = is_encrypted
        self.volume_size = size
        self.snapshot_id = snapshot_id
        self.volume_state = state
        self.iops = iops
        self.volume_type = volume_type
        self.multi_attach_enabled = multi_attach_enabled
        self.is_active = is_active
