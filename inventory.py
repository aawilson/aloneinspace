class InventoryError(Exception): pass


class NotEnoughCapacity(InventoryError):
    def __init__(self, *args, **kwargs):
        if hasattr(kwargs, 'items'):
            self.items = kwargs['items']
            del kwargs['items']
        else:
            self.items = []

        super(NotEnoughCapacity, self).__init__(*args, **kwargs)


class NotEnoughContainerAttachmentPoints(NotEnoughCapacity):
    pass


class Inventory(object):
    """
    this is the class held by an entity that might be interesting, inventory-wise.
    an inventory typically. it has attachment points, but no inherent capacity.
    TODO: some attachment points might have containers that are inherent to the inventory
    ex: a human might have 2 hand containers with a specified bulk capacity
    """
    def __init__(self, container_attachment_points=0, attached_containers=None):
        self.container_attachment_points = container_attachment_points
        self.attached_containers = []
        if attached_containers:
            self.attach_containers(attached_containers)

    def attach_containers(self, *args):
        """accepts containers either as arg list, or as a single iterable argument"""

        if hasattr(args[0], '__iter__'):
            new_containers = list(args[0])
        else:
            new_containers = list(args)

        if len(self.attached_containers) + len(new_containers) > self.container_attachment_points:
            raise NotEnoughContainerAttachmentPoints("Exceeded container attachment points in attach_container", items=new_containers)
        else:
            self.attached_containers = self.attached_containers + list(new_containers)

    def attach_container(self, new_container):
        return self.attach_containers([new_container])


class Item(object):

    def __init__(self, bulk, weight):
        self.bulk = bulk
        self.weight = weight


class Container(Item):
    """
    a container is a special item that can hold other items (including containers)
    its total bulk is the sum of its native bulk, and the bulk of contained items
    """
    # getters and setters here because they're overridden later
    @property
    def bulk(self):
        return self.tare_bulk + self.contained_bulk

    @bulk.setter
    def bulk(self, val):
        self.tare_bulk = val

    @property
    def contained_bulk(self):
        return sum(item.bulk for item in self.items if item)

    @property
    def weight(self):
        return self.tare_weight + self.contained_weight

    @weight.setter
    def weight(self, val):
        self.tare_weight = val

    @property
    def contained_weight(self):
        return sum(item.weight for item in self.items if item)


    def __contains__(self, searched_item):
        return searched_item in self.items or any(searched_item in getattr(item, 'items', []) for item in self.items)

    def __init__(self, bulk_capacity, items=None, bulk=0, weight=0):
        super(Container, self).__init__(bulk, weight)

        self.bulk_capacity = bulk_capacity
        self.items = []

        if items:
            self.add_items(items)

    def add_items(self, *args):
        """accepts items either as arg list, or as a single iterable argument"""
        if hasattr(args[0], '__iter__'):
            new_items = list(args[0])
        else:
            new_items = list(args)

        if sum(item.bulk for item in new_items if item) + self.contained_bulk > self.bulk_capacity:
            raise NotEnoughCapacity("Exceeded capacity in add_items", items=new_items)
        else:
            self.items = self.items + list(new_items)

        return True

    def add_item(self, new_item):
        """convenient alias for add_items"""
        return self.add_items(new_item)


if __name__ == '__main__':
    # items are a thing with weight and bulk
    item1 = Item(bulk=1, weight=5)
    item2 = Item(bulk=1, weight=6)
    item3 = Item(bulk=10, weight=7)

    assert item1.bulk == 1 and item1.weight == 5
    assert item2.bulk == 1 and item2.weight == 6
    assert item3.bulk == 10 and item3.weight == 7

    # containers are also things with weight and bulk
    container1 = Container(bulk_capacity=2, bulk=1, weight=8)

    assert container1.bulk == 1 and container1.weight == 8

    # container bulk is added to with items added
    container1.add_items(item1, item2)

    assert container1.bulk == 1 + item1.bulk + item2.bulk

    assert container1.weight == 8 + item1.weight + item2.weight

    # containers also have a concept of tare (unladen) weight and tare bulk
    assert container1.tare_bulk == 1
    assert container1.tare_weight == 8

    container2 = Container(bulk_capacity=3, bulk=1, weight=9, items=[item1])

    # items can be added to containers
    container2.add_item(item2)
    assert item1 in container2.items
    assert item2 in container2.items
    assert item3 not in container2.items

    # in will check if the item is in the container, or any subcontainers
    assert item1 in container2
    assert item2 in container2
    assert item3 not in container2

    # can try to insert an item, but get it back if no capacity left (with exception)
    try:
        container2.add_item(item3)
    except NotEnoughCapacity, e:
        assert item3 in e.items
        assert item3 not in container2
    else:
        assert False

    # can't initiate a container with more contained bulk than capacity
    try:
        container3 = Container(bulk_capacity=1, bulk=1, weight=10, items=[item3])
    except NotEnoughCapacity, e:
        assert item3 in e.items
    else:
        assert False

    # containers can be nested
    container4 = Container(bulk_capacity=1, bulk=1, weight=11, items=[item1])
    container5 = Container(bulk_capacity=2, bulk=1, weight=12, items=[container4])

    # nested containers propagate information about contents
    assert item1 in container5
    assert item2 not in container5
    assert container4 in container5

    # nested containers sum bulks and weights appropriately
    assert container4.bulk == container4.tare_bulk + item1.bulk
    assert container5.bulk == container5.tare_bulk + container4.bulk

    assert container4.weight == container4.tare_weight + item1.weight
    assert container5.weight == container5.tare_weight + container4.weight

    # inventories are also concepts that exist
    inventory1 = Inventory(container_attachment_points=1)

    # we can attach containers to them
    inventory1.attach_container(container1)

    # we can't attach too many containers to them
    try:
        inventory1.attach_container(container2)
    except NotEnoughContainerAttachmentPoints, e:
        assert container2 in e.items
        assert container2 not in inventory1.attached_containers
    else:
        assert False

    # TODO: retrieve the items
